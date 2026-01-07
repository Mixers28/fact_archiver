import Link from "next/link";
import { getDays } from "./lib/api";

function formatDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

export default async function HomePage() {
  const today = new Date();
  const start = new Date(today);
  start.setDate(start.getDate() - 13);
  const days = await getDays(formatDate(start), formatDate(today));

  return (
    <>
      <section className="hero">
        <span className="pill">Evidence Ledger</span>
        <h1>Fact Archiver</h1>
        <p>
          Daily ledger of claims, artifacts, and status changes. Click a day to review events and
          contested claims.
        </p>
      </section>

      <div className="grid cols-2">
        <div className="card">
          <h3>Recent Days</h3>
          <div className="list">
            {days.days.map((day) => (
              <Link key={day.date} href={`/day/${day.date}`}>
                <div>
                  <strong>{day.date}</strong> — {day.event_count} events
                </div>
              </Link>
            ))}
          </div>
        </div>
        <div className="card">
          <h3>Reviewer Queue</h3>
          <p>
            Jump into the review flow to assess contested and unverified claims from the last two
            weeks.
          </p>
          <Link className="button" href="/review">
            Review Queue
          </Link>
        </div>
      </div>
    </>
  );
}
