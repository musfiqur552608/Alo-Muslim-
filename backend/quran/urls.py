from django.urls import path
from .views import SurahListView, SurahVersesView

urlpatterns = [
    path("surahs/", SurahListView.as_view(), name="surah-list"),
    path("surahs/<int:surah_id>/verses/", SurahVersesView.as_view(), name="surah-verses"),
]