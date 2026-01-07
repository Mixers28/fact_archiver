import Link from "next/link";
import { getDay } from "../../lib/api";

export default async function DayPage({ params }: { params: { date: string } }) {
  const day = await getDay(params.date);

  return (
    <>
      <section className="hero">
        <span className="pill">Daily Ledger</span>
        <h1>{day.date}</h1>
        <p>Events, claims, and review queue for this day.</p>
      </section>

      <div className="grid cols-2">
        <div className="card">
          <h3>Top Events</h3>
          <div className="list">
            {day.events.map((event) => (
              <Link key={event.id} href={`/event/${event.id}`}>
                <div>
                  <strong>{event.title}</strong>
                  {event.importance_score !== null ? ` · ${event.importance_score}` : ""}
                </div>
              </Link>
            ))}
            {day.events.length === 0 && <div>No events yet.</div>}
          </div>
        </div>
        <div className="card">
          <h3>Needs Review</h3>
          <div className="list">
            {day.review_queue.map((claim) => (
              <div key={claim.claim_id}>
                <div>{claim.normalized_text}</div>
                <small>
                  Status: {claim.status} · Score: {claim.score ?? "n/a"}
                </small>
              </div>
            ))}
            {day.review_queue.length === 0 && <div>Nothing in the queue.</div>}
          </div>
          <Link className="button secondary" href="/review">
            Open Review Queue
          </Link>
        </div>
      </div>
    </>
  );
}
