"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Surah = {
    id: number;
    name_arabic: string;
    name_simple: string;
    name_bengali: string;
    verses_count: number;
    revelation_place: string;
};

export default function QuranPage() {
    const [surahs, setSurahs] = useState<Surah[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/surahs/`)
            .then((res) => {
                if (!res.ok) throw new Error();
                return res.json();
            })
            .then(setSurahs)
            .catch(() => setError("সূরার তালিকা আনা যায়নি।"));
    }, []);

    if (error) return <p className="p-8 text-red-600">{error}</p>;
    if (!surahs) return <p className="p-8">লোড হচ্ছে…</p>;

    return (
        <main className="mx-auto max-w-2xl p-8">
            <h1 className="text-2xl font-bold mb-6">আল-কুরআন 📖</h1>
            <ul className="grid gap-3 sm:grid-cols-2">
                {surahs.map((s) => (
                    <li key={s.id}>
                        <Link
                            href={`/quran/${s.id}`}
                            className="flex items-center justify-between rounded-xl border p-4 hover:bg-emerald-50 transition"
                        >
                            <div>
                                <p className="font-semibold">
                                    {s.id}. {s.name_bengali}
                                </p>
                                <p className="text-xs text-gray-500">
                                    {s.verses_count} আয়াত ·{" "}
                                    {s.revelation_place === "makkah" ? "মাক্কী" : "মাদানী"}
                                </p>
                            </div>
                            <span className="text-xl" dir="rtl">{s.name_arabic}</span>
                        </Link>
                    </li>
                ))}
            </ul>
        </main>
    );
}