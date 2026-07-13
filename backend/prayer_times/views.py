from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .services import get_prayer_times, PrayerTimesUnavailable


class PrayerTimesQuerySerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)
    date = serializers.DateField(required=False)


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