from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('administration/manage-patient/',AdminManagePatient.as_view(),name = "admin_manage_patient"),
    path('administration/list-patient/',AdminListPatient.as_view(),name = "admin_list_patient")   
]
