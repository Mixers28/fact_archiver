const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type DaySummary = { date: string; event_count: number };
export type DayResponse = {
  date: string;
  events: { id: string; title: string; importance_score: number | null }[];
  review_queue: {
    claim_id: string;
    event_id: string;
    normalized_text: string;
    status: string;
    score: number | null;
  }[];
};
export type EventResponse = {
  id: string;
  title: string;
  date_key: string;
  sources: {
    id: string;
    publisher: string | null;
    url: string;
    published_at: string | null;
  }[];
  claims_by_status: Record<string, { id: string; normalized_text: string; score: number | null; rationale: string[] }[]>;
};

export async function getDays(start: string, end: string) {
  return fetchJson<{ days: DaySummary[] }>(`/api/days?start=${start}&end=${end}`);
}

export async function getDay(date: string) {
  return fetchJson<DayResponse>(`/api/days/${date}`);
}

export async function getEvent(eventId: string) {
  return fetchJson<EventResponse>(`/api/events/${eventId}`);
}

export async function overrideClaim(
  claimId: string,
  payload: { status: string; score?: number; rationale?: string[] }
) {
  const res = await fetch(`${API_BASE}/api/claims/${claimId}/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Override failed: ${res.status}`);
  }
  return res.json();
}
