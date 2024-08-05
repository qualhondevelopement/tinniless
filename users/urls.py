from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    #Auth APIs
    path('auth/login/',LoginAPI.as_view(),name = "login"),
    path('auth/logout/',LogoutAPIView.as_view(),name = "logout"),
    path('auth/check-if-exists/',IsExisting.as_view(),name = "check_if_exists"),
    # path('auth/signup/',SignupAPI),
    path('auth/send-reset-password-email-link/',PasswordResetRequestView.as_view(),name = "send_reset_password_email_link"),
    path('auth/reset-password/<uidb64>/<token>/',PasswordResetConfirmView.as_view(),name= "reset_password"),
    # path('auth/verify-email/',),
    
    
    # Admin APIs
    path('administration/manage-patient/',AdminManagePatient.as_view(),name = "admin_manage_patient"),
    path('administration/list-patient/',AdminListPatient.as_view(),name = "admin_list_patient"),
    
    path('administration/list-operator/',AdminListOperator.as_view(),name = "list_operator"),
    path('administration/manage-operator/',AdminManageOperator.as_view(),name = "admin-manage-operator"),
    
    path('administration/list-retailer/',AdminListRetailer.as_view(),name = "list_retailer"),
    path('administration/manage-retailer/',AdminManageRetailer.as_view(),name = "admin_manage_retailer"),
    
    path('administration/list-reseller/',AdminListReseller.as_view(),name = "list_reseller"),
    path('administration/manage-reseller/',AdminManageReseller.as_view(),name = "admin_manage_reseller"),
    
    
    
    
    #user api,
    path('user/get-user/',GetuserDetail.as_view(),name= "get_user_detail"),
    
    
]
