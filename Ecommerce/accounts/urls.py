from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('contact/',views.contact,name='contact'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout/', views.user_logout, name='user_logout'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('verify-reset-otp/', views.VerifyResetOTPView.as_view(), name='verify_reset_otp'),
    path('set-new-password/', views.SetNewPasswordView.as_view(), name='set_new_password'),  
    path('profile/edit/', views.create_or_edit_profile, name='create_or_edit_profile'),
    path('profile/detail/', views.profile_detail, name='profile_detail'),
]