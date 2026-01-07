"use client";

import { useState } from "react";
import { overrideClaim } from "../lib/api";

type ReviewItem = {
  claim_id: string;
  normalized_text: string;
  status: string;
  score: number | null;
};

export function ReviewClient({ items }: { items: ReviewItem[] }) {
  const [status, setStatus] = useState("Unverified");
  const [rationale, setRationale] = useState("");
  const [active, setActive] = useState<ReviewItem | null>(items[0] || null);
  const [message, setMessage] = useState("");
  const total = items.length;

  async function handleSubmit() {
    if (!active) {
      return;
    }
    const rationaleList = rationale
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    await overrideClaim(active.claim_id, { status, rationale: rationaleList });
    setMessage("Override saved.");
  }

  return (
    <div className="grid cols-2">
      <div className="card">
        <h3>Queue</h3>
        <p className="meta">{total} items awaiting review</p>
        <div className="list">
          {items.map((item) => {
            const isActive = active?.claim_id === item.claim_id;
            return (
              <button
                key={item.claim_id}
                className={`button secondary${isActive ? " active" : ""}`}
                onClick={() => {
                  setActive(item);
                  setMessage("");
                }}
                aria-label={`Review claim ${item.normalized_text}`}
              >
                {item.normalized_text.slice(0, 64)}
              </button>
            );
          })}
          {items.length === 0 && <p className="meta">No items in the queue.</p>}
        </div>
      </div>
      <div className="card">
        <h3>Override</h3>
        {active ? (
          <>
            <p>{active.normalized_text}</p>
            <p className="meta">
              Selected {items.findIndex((item) => item.claim_id === active.claim_id) + 1} of {total}
            </p>
            <div className="field">
              <label>Status</label>
              <select value={status} onChange={(event) => setStatus(event.target.value)}>
                <option>Unverified</option>
                <option>Corroborated</option>
                <option>Confirmed</option>
                <option>Contested</option>
                <option>Retracted</option>
              </select>
            </div>
            <div className="field">
              <label>Rationale (one per line)</label>
              <textarea
                rows={4}
                value={rationale}
                onChange={(event) => setRationale(event.target.value)}
              />
            </div>
            <button className="button" onClick={handleSubmit}>
              Save Override
            </button>
            {message && <p>{message}</p>}
          </>
        ) : (
          <p className="meta">No claim selected.</p>
        )}
      </div>
    </div>
  );
}
