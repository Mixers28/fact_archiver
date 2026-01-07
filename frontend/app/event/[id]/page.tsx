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
          <p className="meta">{event.sources.length} captured sources</p>
          <div className="list">
            {event.sources.map((source) => (
              <a key={source.id} href={source.url} target="_blank" rel="noreferrer">
                <div>
                  <strong>{source.publisher || "Unknown"}</strong>
                  <div className="meta">{source.published_at || "Published date n/a"}</div>
                </div>
              </a>
            ))}
            {event.sources.length === 0 && (
              <div className="meta">No sources yet. Capture artifacts to populate.</div>
            )}
          </div>
        </div>
        <div className="card">
          <h3>Claims</h3>
          <div className="list">
            {Object.entries(event.claims_by_status).map(([status, claims]) => (
              <div key={status}>
                <div className="meta">
                  <span className={`status-badge ${status.toLowerCase()}`}>{status}</span>
                  <span> · {claims.length} claims</span>
                </div>
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
