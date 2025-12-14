from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('edit-attendance/<int:record_id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/mark', views.mark_attendance, name='mark_attendance'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-balances/', views.manage_balances, name='manage_balances'),
    path('logout/', views.user_logout, name='logout'),
    
    # Event Management URLs
    path('events/', views.events_list, name='events_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Equipment Management URLs
    path('events/<int:event_pk>/equipment/add/', views.equipment_add, name='equipment_add'),
    path('equipment/<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('equipment/<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
]
