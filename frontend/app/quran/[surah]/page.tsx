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

export default function SurahPage() {
    const { surah } = useParams<{ surah: string }>();
    const [verses, setVerses] = useState<Verse[]>([]);
    const [hasNext, setHasNext] = useState(false);
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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
            <div className="space-y-6">
                {verses.map((v) => (
                    <article key={v.verse_key} className="rounded-xl border p-5">
                        <p dir="rtl" className="mb-4 text-right text-3xl leading-loose">
                            {v.arabic}
                        </p>
                        <p className="mb-2 text-sm italic text-gray-500">
                            {v.transliteration}
                        </p>
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