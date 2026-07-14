from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from .services import get_surah_list,get_surah_verses, QuranUnavailable


class SurahListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            return Response(get_surah_list())
        except QuranUnavailable:
            return Response(
                {"detail": "সূরার তালিকা এই মুহূর্তে আনা যাচ্ছে না।"},
                status=503,
            )


class VersesQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, required=False, default=1)


class SurahVersesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, surah_id: int):
        if not 1 <= surah_id <= 114:
            return Response({"detail": "সূরা নম্বর ১-১১৪ এর মধ্যে হতে হবে।"}, status=404)

        query = VersesQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        try:
            result = get_surah_verses(surah_id, page=query.validated_data["page"])
        except QuranUnavailable:
            return Response({"detail": "আয়াত এই মুহূর্তে আনা যাচ্ছে না।"}, status=503)

        return Response(result)