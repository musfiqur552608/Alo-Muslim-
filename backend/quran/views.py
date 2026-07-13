from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_surah_list, QuranUnavailable


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