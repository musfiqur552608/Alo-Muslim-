import requests
from django.core.cache import cache
from .transliterations_bn import SURAH_NAME_BN

QURAN_BASE = "https://api.quran.com/api/v4"
BN_TRANSLATION_ID = 161   
EN_TRANSLATION_ID = 131
VERSES_PER_PAGE = 20


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
            "name_bn_pronunciation": SURAH_NAME_BN.get(c["id"], c["name_simple"]),  # 🆕
            "verses_count": c["verses_count"],
            "revelation_place": c["revelation_place"],
        }
        for c in chapters
    ]

    cache.set(cache_key, result, 60 * 60 * 24 * 7)  
    return result

def get_surah_verses(surah_id: int, page: int = 1) -> dict:
    cache_key = f"quran:verses:{surah_id}:{page}:{BN_TRANSLATION_ID}:{EN_TRANSLATION_ID}"

    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            f"{QURAN_BASE}/verses/by_chapter/{surah_id}",
            params={
                "language": "bn",
                "words": "true",
                "word_fields": "transliteration",
                "translations": f"{BN_TRANSLATION_ID},{EN_TRANSLATION_ID}",
                "fields": "text_uthmani",
                "per_page": VERSES_PER_PAGE,
                "page": page,
            },
            timeout=10,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise QuranUnavailable("Quran.com API unreachable") from exc

    data = resp.json()
    result = {
        "verses": [_reshape_verse(v) for v in data["verses"]],
        "pagination": {
            "current_page": page,
            "total_pages": data["pagination"]["total_pages"],
            "has_next": data["pagination"]["next_page"] is not None,
        },
    }

    cache.set(cache_key, result, 60 * 60 * 24 * 7)
    return result


def _reshape_verse(v: dict) -> dict:
    translations = {t["resource_id"]: t["text"] for t in v["translations"]}

    transliteration = " ".join(
        w["transliteration"]["text"]
        for w in v["words"]
        if w.get("transliteration", {}).get("text")
    )

    return {
        "verse_key": v["verse_key"],            # যেমন "2:255"
        "verse_number": v["verse_number"],
        "arabic": v["text_uthmani"],
        "transliteration": transliteration,      # আপাতত ইংরেজি হরফে
        "translation_bn": translations.get(BN_TRANSLATION_ID, ""),
        "translation_en": translations.get(EN_TRANSLATION_ID, ""),
    }