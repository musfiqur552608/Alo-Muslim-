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
    const [query, setQuery] = useState("");
    const [place, setPlace] = useState<"all" | "makkah" | "madinah">("all");

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

    const q = query.trim().toLowerCase();
    const visibleSurahs = surahs.filter((s) => {
        const matchesQuery =
            q === "" ||
            s.name_bengali.includes(query.trim()) ||
            s.name_simple.toLowerCase().includes(q);

        const matchesPlace = place === "all" || s.revelation_place === place;

        return matchesQuery && matchesPlace;
    });

    return (
        <main className="mx-auto max-w-2xl p-8">
            <h1 className="text-2xl font-bold mb-6">আল-কুরআন 📖</h1>
            <input
                type="text"
                placeholder="সূরা খুঁজুন (বাংলা বা ইংরেজি নামে)…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}             
                className="mb-4 w-full rounded-xl border p-3"
            />

            <div className="mb-6 flex gap-2">
                {(
                    [
                        ["all", "সব"],
                        ["makkah", "মাক্কী"],
                        ["madinah", "মাদানী"],                              
                    ] as const
                ).map(([value, label]) => (
                    <button
                        key={value}
                        onClick={() => setPlace(value)}                    
                        className={`rounded-full border px-4 py-1 text-sm ${place === value ? "bg-emerald-600 text-white" : "hover:bg-emerald-50"
                            }`}
                    >
                        {label}
                    </button>
                ))}
            </div>
            <ul className="grid gap-3 sm:grid-cols-2">
                {visibleSurahs.map((s) => (
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