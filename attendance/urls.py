from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('view-attendance/', views.view_attendance, name='view_attendance'),
    path('edit-attendance/<int:record_id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/mark',views.mark_attendance, name='mark_attendance'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]
