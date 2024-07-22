from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    #Auth APIs
    path('auth/login/',LoginAPI.as_view(),name = "login"),
    # path('auth/signup/',SignupAPI),
    path('auth/send-reset-password-email-link/',PasswordResetRequestView.as_view(),name = "send_reset_password_email_link"),
    path('auth/reset-password/<uidb64>/<token>/',PasswordResetConfirmView.as_view(),name= "reset_password"),
    # path('auth/verify-email/',),
    
    
    # Admin APIs
    path('administration/manage-patient/',AdminManagePatient.as_view(),name = "admin_manage_patient"),
    path('administration/list-patient/',AdminListPatient.as_view(),name = "admin_list_patient"),
    # path('administration/manage-operator/'),
    # path('administration/list-operator/'),
    
]
