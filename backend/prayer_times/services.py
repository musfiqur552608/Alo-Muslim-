import requests
from django.core.cache import cache
from core.models import SiteConfig

adjustment = SiteConfig.load().hijri_adjustment

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
    
def get_prayer_times_by_city(city: str, country: str, date_str: str) -> dict:
    city_key = city.strip().lower()
    country_key = country.strip().lower()
    cache_key = f"prayer:city:{date_str}:{city_key}:{country_key}:{DEFAULT_METHOD}:{DEFAULT_SCHOOL}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            f"{ALADHAN_BASE}/timingsByCity/{date_str}",
            params={
                "city": city,
                "country": country,
                "method": DEFAULT_METHOD,
                "school": DEFAULT_SCHOOL,
            },
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise PrayerTimesUnavailable("AlAdhan API unreachable") from exc

    result = _reshape(resp.json()["data"])
    cache.set(cache_key, result, 60 * 60 * 24 * 30)
    return result

def get_ramadan_calendar(lat: float, lng: float, hijri_year: int) -> list[dict]:
    lat_r, lng_r = round(lat, 2), round(lng, 2)
    adjustment = SiteConfig.load().hijri_adjustment
    cache_key = (
        f"ramadan:{hijri_year}:{lat_r}:{lng_r}"
        f":{DEFAULT_METHOD}:{DEFAULT_SCHOOL}:{adjustment}"
    )

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            f"{ALADHAN_BASE}/hijriCalendar/{hijri_year}/9",   # ৯ = রমজান
            params={
                "latitude": lat_r,
                "longitude": lng_r,
                "method": DEFAULT_METHOD,
                "school": DEFAULT_SCHOOL,
                "adjustment": adjustment,
            },
            timeout=10,        # ৩০ দিনের ডেটা — একটু বেশি সময় দিলাম
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise PrayerTimesUnavailable("AlAdhan API unreachable") from exc

    days = resp.json()["data"]
    result = [
        {
            "hijri_day": d["date"]["hijri"]["day"],
            "gregorian_date": d["date"]["gregorian"]["date"],
            "weekday_en": d["date"]["gregorian"]["weekday"]["en"],
            "sehri_ends": d["timings"]["Imsak"].split(" ")[0],
            "iftar": d["timings"]["Maghrib"].split(" ")[0],
        }
        for d in days
    ]

    cache.set(cache_key, result, 60 * 60 * 24 * 7)   # ৭ দিন
    return result