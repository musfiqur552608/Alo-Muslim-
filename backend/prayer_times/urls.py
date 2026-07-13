from django.urls import path
from .views import PrayerTimesView

urlpatterns = [
    path("prayer-times/", PrayerTimesView.as_view(), name="prayer-times"),
]