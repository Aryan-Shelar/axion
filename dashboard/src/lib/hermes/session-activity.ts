import type { HermesSessionSummary } from "./types";

const validTimestamp = (value?: string): number | null => {
  if (!value) return null;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
};

export function sortSessionsNewestFirst(sessions: readonly HermesSessionSummary[]): HermesSessionSummary[] {
  return sessions.map((session, index) => ({ session, index, timestamp: validTimestamp(session.updatedAt) }))
    .sort((left, right) => {
      if (left.timestamp !== null && right.timestamp !== null) return right.timestamp - left.timestamp || left.index - right.index;
      if (left.timestamp !== null) return -1;
      if (right.timestamp !== null) return 1;
      return left.index - right.index;
    })
    .map(({ session }) => session);
}

export function sessionSecondaryText(session: HermesSessionSummary): string | null {
  return session.source ?? session.status ?? null;
}

export function formatSessionUpdatedAt(value?: string): string | null {
  if (!value) return null;
  const timestamp = validTimestamp(value);
  return timestamp === null ? value : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(timestamp);
}
