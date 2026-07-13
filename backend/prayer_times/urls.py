from django.urls import path
from .views import PrayerTimesView, RamadanCalendarView

urlpatterns = [
    path("prayer-times/", PrayerTimesView.as_view(), name="prayer-times"),
    path("ramadan-calendar/", RamadanCalendarView.as_view(), name="ramadan-calendar"),
]