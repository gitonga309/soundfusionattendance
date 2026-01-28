"""
M-Pesa STK Push Integration Utilities
Handles M-Pesa STK push requests, callbacks, and payment processing
"""
import base64
import json
import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import MpesaPayment, EmailNotification
import logging

logger = logging.getLogger(__name__)


class MpesaClient:
    """M-Pesa API client for STK push and payment operations"""
    
    # API Endpoints
    AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    QUERY_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    
    # Production URLs (when environment is set to production)
    AUTH_URL_PROD = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL_PROD = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    QUERY_URL_PROD = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.business_short_code = settings.MPESA_BUSINESS_SHORT_CODE
        self.pass_key = settings.MPESA_PASS_KEY
        self.environment = settings.MPESA_ENVIRONMENT
        self.access_token = None
        
        # Set URLs based on environment
        if self.environment == 'production':
            self.auth_url = self.AUTH_URL_PROD
            self.stk_push_url = self.STK_PUSH_URL_PROD
            self.query_url = self.QUERY_URL_PROD
        else:
            self.auth_url = self.AUTH_URL
            self.stk_push_url = self.STK_PUSH_URL
            self.query_url = self.QUERY_URL
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            response = requests.get(
                self.auth_url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=10
            )
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get M-Pesa access token: {str(e)}")
            raise
    
    def initiate_stk_push(self, user, phone_number, amount, payment_purpose, payment_id=None):
        """
        Initiate STK push to collect payment from customer
        
        Args:
            user: User object requesting payment
            phone_number: Customer phone number in format 254xxxxxxxxx
            amount: Amount in KSH
            payment_purpose: Description of payment
            payment_id: Optional payment record ID
            
        Returns:
            dict: Response containing checkout_request_id and other details
        """
        try:
            # Get access token
            if not self.access_token:
                self.get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{self.business_short_code}{self.pass_key}{timestamp}".encode()
            ).decode()
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_short_code,
                "PhoneNumber": phone_number,
                "CallBackURL": settings.MPESA_CALLBACK_URL,
                "AccountReference": f"Payment_{payment_id or user.id}_{timestamp}",
                "TransactionDesc": payment_purpose[:20]  # Limited to 20 chars
            }
            
            # Make request
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.stk_push_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            # Create payment record if successful
            if response_data.get('ResponseCode') == '0':
                payment = MpesaPayment.objects.create(
                    user=user,
                    phone_number=phone_number,
                    amount=amount,
                    payment_purpose=payment_purpose,
                    checkout_request_id=response_data.get('CheckoutRequestID'),
                    merchant_request_id=response_data.get('MerchantRequestID'),
                    status='pending'
                )
                
                logger.info(f"STK push initiated for {user.username}: {payment.id}")
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'checkout_request_id': response_data.get('CheckoutRequestID'),
                    'merchant_request_id': response_data.get('MerchantRequestID'),
                    'message': response_data.get('ResponseDescription')
                }
            else:
                logger.warning(f"STK push failed for {user.username}: {response_data}")
                return {
                    'success': False,
                    'message': response_data.get('ResponseDescription', 'Failed to initiate payment'),
                    'error_code': response_data.get('ResponseCode')
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating STK push: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to connect to M-Pesa service. Please try again.',
                'error': str(e)
            }
    
    def query_payment_status(self, checkout_request_id):
        """Query the status of an STK push request"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{self.business_short_code}{self.pass_key}{timestamp}".encode()
            ).decode()
            
            payload = {
                "BusinessShortCode": self.business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.query_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying payment status: {str(e)}")
            return {'error': str(e)}


def process_mpesa_callback(request_data):
    """
    Process M-Pesa callback from STK push
    
    Args:
        request_data: Callback data from M-Pesa
    """
    try:
        data = request_data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = data.get('CheckoutRequestID')
        result_code = data.get('ResultCode')
        result_description = data.get('ResultDesc')
        merchant_request_id = data.get('MerchantRequestID')
        
        # Find payment record
        try:
            payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
        except MpesaPayment.DoesNotExist:
            logger.warning(f"Callback received for unknown checkout ID: {checkout_request_id}")
            return False
        
        # Update payment record based on result
        if result_code == 0:  # Success
            payment.status = 'completed'
            payment.result_code = result_code
            payment.result_description = result_description
            payment.merchant_request_id = merchant_request_id
            payment.completed_at = timezone.now()
            
            # Extract callback data if available
            callback_metadata = data.get('CallbackMetadata', {}).get('Item', [])
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    payment.receipt_number = item.get('Value')
                elif item.get('Name') == 'TransactionDate':
                    payment.transaction_date = item.get('Value')
            
            payment.save()
            
            # Send confirmation email
            send_payment_confirmation_email(payment)
            
            logger.info(f"Payment {payment.id} completed successfully")
            return True
        else:
            # Payment failed or was cancelled
            payment.status = 'failed'
            payment.result_code = result_code
            payment.result_description = result_description
            payment.save()
            
            logger.warning(f"Payment {payment.id} failed: {result_description}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing M-Pesa callback: {str(e)}")
        return False


def send_payment_confirmation_email(payment):
    """Send confirmation email after successful payment"""
    try:
        notification = EmailNotification.objects.create(
            recipient=payment.user.email,
            user=payment.user,
            notification_type='payment_approved',
            subject=f'Payment Confirmation - KSH {payment.amount}',
            message=f"""
            Dear {payment.user.get_full_name() or payment.user.username},
            
            Your payment has been successfully received.
            
            Payment Details:
            - Amount: KSH {payment.amount}
            - Purpose: {payment.payment_purpose}
            - Receipt Number: {payment.receipt_number or 'Processing'}
            - Date: {payment.transaction_date or 'Just now'}
            
            Thank you for using Sound Fusion Attendance System.
            
            Best regards,
            Sound Fusion Admin Team
            """
        )
        
        # Send email asynchronously if celery is configured
        send_email.delay(notification.id)
        
    except Exception as e:
        logger.error(f"Error creating payment confirmation email: {str(e)}")


# Celery task (if celery is configured)
def send_email(notification_id):
    """Send email notification"""
    try:
        from django.core.mail import send_mail
        
        notification = EmailNotification.objects.get(id=notification_id)
        
        send_mail(
            notification.subject,
            notification.message,
            settings.DEFAULT_FROM_EMAIL,
            [notification.recipient],
            fail_silently=False,
        )
        
        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.save()
        
        logger.info(f"Email sent to {notification.recipient}")
        
    except Exception as e:
        notification.failed_attempts += 1
        notification.last_error = str(e)
        notification.save()
        logger.error(f"Error sending email: {str(e)}")
