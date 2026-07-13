"use client";

import { useEffect, useState } from "react";

type RamadanDay = {
    hijri_day: string;
    gregorian_date: string;
    weekday_en: string;
    sehri_ends: string;
    iftar: string;
};

export default function RamadanPage() {
    const [days, setDays] = useState<RamadanDay[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                try {
                    const res = await fetch(
                        `${process.env.NEXT_PUBLIC_API_URL}/ramadan-calendar/` +
                        `?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`
                    );
                    if (!res.ok) throw new Error();
                    setDays(await res.json());
                } catch {
                    setError("রমজান ক্যালেন্ডার আনা যায়নি।");
                }
            },
            () => setError("লোকেশন অনুমতি প্রয়োজন।")
        );
    }, []);

    if (error) return <p className="p-8 text-red-600">{error}</p>;
    if (!days) return <p className="p-8">লোড হচ্ছে…</p>;

    const today = new Date();
    const todayStr = `${String(today.getDate()).padStart(2, "0")}-${String(
        today.getMonth() + 1
    ).padStart(2, "0")}-${today.getFullYear()}`;
         

    return (
        <main className="mx-auto max-w-2xl p-8">
            <h1 className="text-2xl font-bold mb-6">রমজান সময়সূচি 🌙</h1>
            <table className="w-full rounded-xl border text-sm">
                <thead className="bg-emerald-600 text-white">
                    <tr>
                        <th className="p-3 text-left">রোজা</th>
                        <th className="p-3 text-left">তারিখ</th>
                        <th className="p-3 text-right">সেহরি শেষ</th>
                        <th className="p-3 text-right">ইফতার</th>
                    </tr>
                </thead>
                <tbody className="divide-y">
                    {days.map((d) => (
                        <tr
                            key={d.hijri_day}
                            className={d.gregorian_date === todayStr ? "bg-emerald-50 font-semibold" : ""}
                        >
                            <td className="p-3">{d.hijri_day}</td>
                            <td className="p-3">
                                {d.gregorian_date}{" "}
                                <span className="text-gray-400">({d.weekday_en})</span>
                            </td>
                            <td className="p-3 text-right font-mono">{d.sehri_ends}</td>
                            <td className="p-3 text-right font-mono">{d.iftar}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </main>
    );
}