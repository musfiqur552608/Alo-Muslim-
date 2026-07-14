from django.urls import path
from .views import SurahAudioView, SurahListView, SurahVersesView

urlpatterns = [
    path("surahs/", SurahListView.as_view(), name="surah-list"),
    path("surahs/<int:surah_id>/verses/", SurahVersesView.as_view(), name="surah-verses"),
    path("surahs/<int:surah_id>/audio/", SurahAudioView.as_view(), name="surah-audio"),
]