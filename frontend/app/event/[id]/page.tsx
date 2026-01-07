import Link from "next/link";
import { getEvent } from "../../lib/api";

export default async function EventPage({ params }: { params: { id: string } }) {
  const event = await getEvent(params.id);

  return (
    <>
      <section className="hero">
        <span className="pill">Event</span>
        <h1>{event.title}</h1>
        <p>Date: {event.date_key}</p>
      </section>

      <div className="grid cols-2">
        <div className="card">
          <h3>Sources</h3>
          <div className="list">
            {event.sources.map((source) => (
              <a key={source.id} href={source.url} target="_blank" rel="noreferrer">
                {source.publisher || "Unknown"} · {source.published_at || "n/a"}
              </a>
            ))}
            {event.sources.length === 0 && <div>No sources yet.</div>}
          </div>
        </div>
        <div className="card">
          <h3>Claims</h3>
          <div className="list">
            {Object.entries(event.claims_by_status).map(([status, claims]) => (
              <div key={status}>
                <strong>{status}</strong>
                <div>
                  {claims.map((claim) => (
                    <div key={claim.id}>
                      {claim.normalized_text}
                      {claim.score !== null ? ` · ${claim.score}` : ""}
                    </div>
                  ))}
                </div>
              </div>
            ))}
            {Object.keys(event.claims_by_status).length === 0 && <div>No claims yet.</div>}
          </div>
          <Link className="button secondary" href="/review">
            Review Claims
          </Link>
        </div>
      </div>
    </>
  );
}
