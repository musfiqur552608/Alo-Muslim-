import requests
from django.core.cache import cache

ALADHAN_BASE = "https://api.aladhan.com/v1"


DEFAULT_METHOD = 1
DEFAULT_SCHOOL = 1   # Hanafi (আসরের সময় হিসাবের জন্য)


class PrayerTimesUnavailable(Exception):
    pass


def get_prayer_times(lat: float, lng: float, date_str: str) -> dict:
    lat_r, lng_r = round(lat, 2), round(lng, 2)
    cache_key = f"prayer:{date_str}:{lat_r}:{lng_r}:{DEFAULT_METHOD}:{DEFAULT_SCHOOL}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            f"{ALADHAN_BASE}/timings/{date_str}",
            params={
                "latitude": lat_r,
                "longitude": lng_r,
                "method": DEFAULT_METHOD,
                "school": DEFAULT_SCHOOL,
            },
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise PrayerTimesUnavailable("AlAdhan API unreachable") from exc

    data = resp.json()["data"]
    result = _reshape(data)

    cache.set(cache_key, result, 60 * 60 * 24 * 30)  # ৩০ দিন
    return result


def _reshape(data: dict) -> dict:
    """AlAdhan-এর বিশাল রেসপন্স থেকে শুধু দরকারি অংশ।"""
    t = data["timings"]
    hijri = data["date"]["hijri"]
    return {
        "timings": {
            "fajr": t["Fajr"],
            "sunrise": t["Sunrise"],
            "dhuhr": t["Dhuhr"],
            "asr": t["Asr"],
            "maghrib": t["Maghrib"],
            "isha": t["Isha"],
        },
        "hijri": {
            "day": hijri["day"],
            "month_en": hijri["month"]["en"],
            "month_ar": hijri["month"]["ar"],
            "year": hijri["year"],
        },
        "gregorian_date": data["date"]["gregorian"]["date"],
    }