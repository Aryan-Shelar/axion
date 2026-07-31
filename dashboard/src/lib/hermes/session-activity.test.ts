import { describe, expect, it } from "vitest";
import type { HermesSessionSummary } from "./types";
import { sessionSecondaryText, sortSessionsNewestFirst } from "./session-activity";

const session = (id: string, updatedAt?: string): HermesSessionSummary => ({ id, title: id, ...(updatedAt ? { updatedAt } : {}) });

describe("sortSessionsNewestFirst", () => {
  it("sorts valid timestamps descending before undated sessions", () => {
    const input = [session("missing"), session("old", "2026-07-29T10:00:00Z"), session("new", "2026-07-31T10:00:00Z")];
    expect(sortSessionsNewestFirst(input).map(({ id }) => id)).toEqual(["new", "old", "missing"]);
    expect(input.map(({ id }) => id)).toEqual(["missing", "old", "new"]);
  });

  it("preserves original order for equal, invalid, and missing timestamps", () => {
    const input = [session("equal-a", "2026-07-31T10:00:00Z"), session("invalid-a", "not-a-date"), session("missing-a"), session("equal-b", "2026-07-31T10:00:00Z"), session("invalid-b", "also-invalid"), session("missing-b")];
    expect(sortSessionsNewestFirst(input).map(({ id }) => id)).toEqual(["equal-a", "equal-b", "invalid-a", "missing-a", "invalid-b", "missing-b"]);
  });
});

it("prefers source over status for secondary display text", () => {
  expect(sessionSecondaryText({ id: "1", title: "One", source: "cli", status: "active" })).toBe("cli");
  expect(sessionSecondaryText({ id: "2", title: "Two", status: "idle" })).toBe("idle");
  expect(sessionSecondaryText({ id: "3", title: "Three" })).toBeNull();
});
