import { getDay } from "../lib/api";
import { ReviewClient } from "./ReviewClient";

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

export default async function ReviewPage() {
  const day = await getDay(todayKey());
  return (
    <>
      <section className="hero">
        <span className="pill">Reviewer</span>
        <h1>Review Queue</h1>
        <p>Override claim statuses and add rationale.</p>
      </section>
      <ReviewClient
        items={day.review_queue.map((item) => ({
          claim_id: item.claim_id,
          normalized_text: item.normalized_text,
          status: item.status,
          score: item.score,
        }))}
      />
    </>
  );
}
