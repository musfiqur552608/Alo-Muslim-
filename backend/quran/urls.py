from django.urls import path
from .views import SurahListView

urlpatterns = [
    path("surahs/", SurahListView.as_view(), name="surah-list"),
]