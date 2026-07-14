"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type Verse = {
    verse_key: string;
    verse_number: number;
    arabic: string;
    transliteration: string;
    translation_bn: string;
    translation_en: string;
};

type VersesResponse = {
    verses: Verse[];
    pagination: { current_page: number; total_pages: number; has_next: boolean };
};

// Same shape as the Surah type on the list page (lesson 4).
type Surah = {
    id: number;
    name_arabic: string;
    name_simple: string;
    name_bengali: string;
    verses_count: number;
    revelation_place: string;
    name_bn_pronunciation: string;
};

export default function SurahPage() {
    const { surah } = useParams<{ surah: string }>();
    const [surahInfo, setSurahInfo] = useState<Surah | null>(null);
    const [verses, setVerses] = useState<Verse[]>([]);
    const [hasNext, setHasNext] = useState(false);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showTranslit, setShowTranslit] = useState(true);

    // Fetch the surah list once and pick out this surah for the header.
    // The list is small (114 items) and server-cached, so no new endpoint needed.
    useEffect(() => {
        setVerses([]);      // পুরনো সূরার আয়াত মুছে দাও
        setPage(1);
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/surahs/`)
            .then((res) => {
                if (!res.ok) throw new Error();
                return res.json();
            })
            .then((data: Surah[]) => {
                // `surah` from useParams is a string ("2"); s.id is a number (2).
                // s.id === surah would be 2 === "2" → false, so compare as strings.
                setSurahInfo(data.find((s) => String(s.id) === surah) ?? null);
            })
            .catch(() => {
                // Header is optional — ignore if the list fetch fails.
            });
    }, [surah]);

    useEffect(() => {
        setLoading(true);
        fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/surahs/${surah}/verses/?page=${page}`
        )
            .then((res) => {
                if (!res.ok) throw new Error();
                return res.json();
            })
            .then((data: VersesResponse) => {
                setVerses((prev) =>
                    page === 1 ? data.verses : [...prev, ...data.verses]
                );
                setHasNext(data.pagination.has_next);
            })
            .catch(() => setError("আয়াত আনা যায়নি।"))
            .finally(() => setLoading(false));
    }, [surah, page]);

    if (error) return <p className="p-8 text-red-600">{error}</p>;

    return (
        <main className="mx-auto max-w-2xl p-8">
            {surahInfo && (
                <header className="mb-8 rounded-xl border p-5 text-center">
                    <p className="mb-1 text-3xl" dir="rtl">
                        {surahInfo.name_arabic}
                    </p>
                    <h1 className="text-xl font-bold">
                        {surahInfo.id}. {surahInfo.name_bn_pronunciation}
                    </h1>
                    <p className="mt-1 text-sm text-gray-500">
                        অর্থ: {surahInfo.name_bengali} · {surahInfo.verses_count} আয়াত ·{" "}
                        {surahInfo.revelation_place === "makkah" ? "মাক্কী" : "মাদানী"}
                    </p>
                </header>
            )}

            <div className="mb-6 flex justify-end">
                <label className="flex items-center gap-2 text-sm text-gray-600">
                    <span aria-hidden>⚙️</span>
                    <input
                        type="checkbox"
                        checked={showTranslit}
                        onChange={(e) => setShowTranslit(e.target.checked)}
                    />
                    উচ্চারণ দেখাও
                </label>
            </div>

            <div className="space-y-6">
                {verses.map((v) => (
                    <article key={v.verse_key} className="rounded-xl border p-5">
                        <p dir="rtl" className="mb-4 text-right text-3xl leading-loose">
                            {v.arabic}
                        </p>
                        {showTranslit && (
                            <p className="mb-2 text-sm italic text-gray-500">
                                {v.transliteration}
                            </p>
                        )}
                        <p className="mb-2">{v.translation_bn}</p>
                        <p className="text-sm text-gray-600">{v.translation_en}</p>
                        <p className="mt-3 text-xs text-gray-400">{v.verse_key}</p>
                    </article>
                ))}
            </div>

            {loading && <p className="p-4 text-center">লোড হচ্ছে…</p>}

            {hasNext && !loading && (
                <button
                    onClick={() => setPage((p) => p + 1)}
                    className="mt-6 w-full rounded-xl border p-3 hover:bg-emerald-50"
                >
                    আরও আয়াত দেখুন
                </button>
            )}
        </main>
    );
}