from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('get-location-data/',GetLocation.as_view(), name = "get_location_data"),
    path('get-tinnitus-types/',GetAllTinitusTypes.as_view(), name = "get_all_tinnitus_types"),
    path('get-lang-list/',GetAllLanguage.as_view(),name = "get_all_lang"),
    path('get-doc-types/',GetTaxDocumentTypes.as_view(),name = "Get_doc_types"),
    path('manage-settings/',ManageSettings.as_view(),name = "manage_settings"),
    path('manage-feedback/',ManageFeedback.as_view(),name = "manage_feedback"),
    path('get-feedback-list/',GetFeedbackList.as_view(),name = "get_feedback_list"),
    path('manage-music-category/',ManageMusicCategory.as_view(),name = "manage_music_category"),
    path('get-music-category-list/',GetMusicCategoryList.as_view(),name = "get_music_category_list"),
    path('manage-music-files/',ManageMusicFiles.as_view(),name = "manage_music_files"),
    path('get-music-files-list/',GetMusicFilesList.as_view(),name = "get_music_files_list"),
]