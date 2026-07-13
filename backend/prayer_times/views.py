from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .services import get_prayer_times, PrayerTimesUnavailable, get_ramadan_calendar


class PrayerTimesQuerySerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90, required=False)
    lng = serializers.FloatField(min_value=-180, max_value=180, required=False)
    city = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    date = serializers.DateField(required=False)

    def validate(self, attrs):
        has_coords = "lat" in attrs and "lng" in attrs
        has_city = "city" in attrs and "country" in attrs
        if not has_coords and not has_city:
            raise serializers.ValidationError(
                "হয় lat+lng, নয়তো city+country দিতে হবে।"
            )
        return attrs


class PrayerTimesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = PrayerTimesQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        date = query.validated_data.get("date") or timezone.localdate()
        date_str = date.strftime("%d-%m-%Y")   # AlAdhan-এর ফরম্যাট

        try:
            result = get_prayer_times(
                lat=query.validated_data["lat"],
                lng=query.validated_data["lng"],
                date_str=date_str,
            )
        except PrayerTimesUnavailable:
            return Response(
                {"detail": "নামাজের সময় এই মুহূর্তে আনা যাচ্ছে না।"},
                status=503,
            )

        return Response(result)
    
class RamadanQuerySerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)   
    lng = serializers.FloatField(min_value=-180, max_value=180)
    hijri_year = serializers.IntegerField(required=False)


class RamadanCalendarView(APIView):
    permission_classes = [AllowAny]                                    

    def get(self, request):
        query = RamadanQuerySerializer(data=request.query_params)         
        query.is_valid(raise_exception=True)

        lat = query.validated_data["lat"]
        lng = query.validated_data["lng"]

        hijri_year = query.validated_data.get("hijri_year")
        if hijri_year is None:
    
            today_str = timezone.localdate().strftime("%d-%m-%Y")
            current = get_prayer_times(lat=lat, lng=lng, date_str=today_str)
            hijri_year = int(current["hijri"]["year"])            

        try:
            result = get_ramadan_calendar(lat=lat, lng=lng, hijri_year=hijri_year) 
        except PrayerTimesUnavailable:
            return Response(
                {"detail": "রমজান ক্যালেন্ডার এই মুহূর্তে আনা যাচ্ছে না।"},
                status=503,                                       
            )

        return Response(result)