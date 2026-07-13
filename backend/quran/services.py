import requests
from django.core.cache import cache

QURAN_BASE = "https://api.quran.com/api/v4"
BN_TRANSLATION_ID = 161   


class QuranUnavailable(Exception):
    pass


def get_surah_list() -> list[dict]:
    cache_key = "quran:chapters:bn"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            f"{QURAN_BASE}/chapters",
            params={"language": "bn"},
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise QuranUnavailable("Quran.com API unreachable") from exc

    chapters = resp.json()["chapters"]
    result = [
        {
            "id": c["id"],
            "name_arabic": c["name_arabic"],
            "name_simple": c["name_simple"],
            "name_bengali": c["translated_name"]["name"],
            "verses_count": c["verses_count"],
            "revelation_place": c["revelation_place"],
        }
        for c in chapters
    ]

    cache.set(cache_key, result, 60 * 60 * 24 * 7)  
    return result