from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('get-location-data/',GetLocation.as_view(), name = "get_location_data"),
    path('get-tinnitus-types/',GetAllTinitusTypes.as_view(), name = "get_all_tinnitus_types")
]