from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('employment-type/', views.employment_type_selection, name='employment_type_selection'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
    path('onboarding/status/', views.onboarding_status, name='onboarding_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/mark-payment/', views.mark_payment, name='mark_payment'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('edit-attendance/<int:record_id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/mark', views.mark_attendance, name='mark_attendance'),
    path('api/events/', views.get_events, name='get_events'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-balances/', views.manage_balances, name='manage_balances'),
    path('admin/user-attendance-history/<int:user_id>/', views.view_user_attendance_history, name='view_user_attendance_history'),
    path('admin/reimbursement/<int:reimbursement_id>/action/', views.reimbursement_action, name='reimbursement_action'),
    path('logout/', views.user_logout, name='logout'),
    
    # Event Management URLs
    path('events/', views.events_list, name='events_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Expense Reimbursement URLs
    path('reimbursement/submit/', views.submit_reimbursement, name='submit_reimbursement'),
    path('reimbursement/view/', views.view_reimbursements, name='view_reimbursements'),
    path('admin/reimbursements/', views.admin_reimbursements, name='admin_reimbursements'),
    path('admin/reimbursement/<int:reimbursement_id>/approve/', views.approve_reimbursement, name='approve_reimbursement'),
    path('admin/reimbursement/<int:reimbursement_id>/reject/', views.reject_reimbursement, name='reject_reimbursement'),
    path('admin/reimbursement/<int:reimbursement_id>/send-stk/', views.send_reimbursement_stk_push, name='send_reimbursement_stk_push'),
    path('admin/reimbursement/<int:reimbursement_id>/confirm-payment/', views.confirm_reimbursement_payment, name='confirm_reimbursement_payment'),
    
    # M-Pesa Payment URLs
    path('api/mpesa/request-payment/', views.request_mpesa_payment, name='request_mpesa_payment'),
    path('api/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('api/mpesa/payment-status/', views.check_payment_status, name='check_payment_status'),
    
    # STK Push Modal URLs (not under /admin/ to avoid admin catch-all)
    path('payment/stk-push/', views.stk_push_modal, name='stk_push_modal'),
    path('api/stk-status/', views.check_stk_status, name='check_stk_status'),
    
    # Crew Assignments
    path('my-assignments/', views.my_assignments, name='my_assignments'),
]