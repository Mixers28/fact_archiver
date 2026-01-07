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
  const totalEvents = days.days.reduce((sum, day) => sum + day.event_count, 0);

  return (
    <>
      <section className="hero">
        <span className="pill">Evidence Ledger</span>
        <h1>Fact Archiver</h1>
        <p>
          A daily ledger of claims, artifacts, and status changes. Start with recent days or jump
          straight to the review queue.
        </p>
        <div className="stats">
          <div className="stat">
            <strong>{totalEvents}</strong>
            <div className="meta">Events (last 14 days)</div>
          </div>
          <div className="stat">
            <strong>{days.days.length}</strong>
            <div className="meta">Days tracked</div>
          </div>
        </div>
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
            {days.days.length === 0 && <div className="meta">No days ingested yet.</div>}
          </div>
        </div>
        <div className="card">
          <h3>Review Queue</h3>
          <p>
            Assess contested and unverified claims from the last two weeks.
          </p>
          <Link className="button" href="/review">
            Review Queue
          </Link>
        </div>
      </div>
    </>
  );
}
