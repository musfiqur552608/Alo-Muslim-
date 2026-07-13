"use client";

import { useEffect, useState } from "react";

type PrayerData = {
  timings: Record<string, string>;
  hijri: { day: string; month_en: string; month_ar: string; year: string };
  gregorian_date: string;
};

const WAQT_NAMES: Record<string, string> = {
  fajr: "ফজর", sunrise: "সূর্যোদয়", dhuhr: "যোহর",
  asr: "আসর", maghrib: "মাগরিব", isha: "এশা",
};

export default function PrayerTimesPage() {
  const [data, setData] = useState<PrayerData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 🆕 হেল্পার ১: রেসপন্স হ্যান্ডলিং এক জায়গায়
    const loadData = async (url: string) => {
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error();
        setData(await res.json());
      } catch {
        setError("নামাজের সময় আনা যায়নি। পরে আবার চেষ্টা করুন।");
      }
    };

    // 🆕 হেল্পার ২: শহর দিয়ে আনা (fallback-এর জন্য)
    const fetchByCity = (city: string, country: string) =>
      loadData(
        `${process.env.NEXT_PUBLIC_API_URL}/prayer-times/?city=${city}&country=${country}`
      );

    navigator.geolocation.getCurrentPosition(
      (pos) =>
        loadData(
          `${process.env.NEXT_PUBLIC_API_URL}/prayer-times/` +
          `?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`
        ),
      // 🆕 আগে এখানে ছিল: () => setError("লোকেশন অনুমতি প্রয়োজন।")
      // এখন error-এর বদলে ঢাকার সময় দেখাই:
      () => fetchByCity("Dhaka", "Bangladesh")
    );
  }, []);

  if (error) return <p className="p-8 text-red-600">{error}</p>;
  if (!data) return <p className="p-8">লোড হচ্ছে…</p>;

  // 🆕 হাইলাইট লজিক — এখানে বসবে, কারণ:
  // hooks-এর পরে, কিন্তু return-এর আগে। data null-চেক পেরিয়ে
  // এসেছি, তাই data.timings নিরাপদে পড়া যায়।
  const now = new Date();
  const nowHM = `${String(now.getHours()).padStart(2, "0")}:${String(
    now.getMinutes()
  ).padStart(2, "0")}`;

  const prayerKeys = ["fajr", "dhuhr", "asr", "maghrib", "isha"];
  const nextWaqt =
    prayerKeys.find((k) => data.timings[k] > nowHM) ?? "fajr";

  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="text-2xl font-bold mb-1">আজকের নামাজের সময়</h1>
      <p className="text-sm text-gray-500 mb-6">
        {data.hijri.day} {data.hijri.month_en} {data.hijri.year} হিজরি
      </p>
      <ul className="divide-y rounded-xl border">
        {Object.entries(data.timings).map(([key, time]) => (
          <li
            key={key}
            // 🆕 আগে ছিল: className="flex justify-between p-4"
            className={`flex justify-between p-4 ${key === nextWaqt ? "bg-emerald-50 font-semibold" : ""
              }`}
          >
            <span>{WAQT_NAMES[key]}</span>
            <span className="font-mono">{time}</span>
          </li>
        ))}
      </ul>
    </main>
  );
}