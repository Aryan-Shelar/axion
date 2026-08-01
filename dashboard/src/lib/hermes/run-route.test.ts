import { describe, expect, it } from "vitest";
import { parseApprovalRequest, parseCreateRunRequest, validateJsonWrite } from "./run-route";

const request = (body: string, headers: Record<string, string> = { "content-type": "application/json" }) => new Request("http://localhost/api/hermes/runs", { method: "POST", body, headers });

describe("Hermes run route validation", () => {
  it("accepts only the exact trimmed creation shape", async () => {
    const value = await validateJsonWrite(request(JSON.stringify({ skillId: "verified-ai-radar", task: "  do it  ", idempotencyKey: "550e8400-e29b-41d4-a716-446655440000" })), ["skillId", "task", "idempotencyKey"]);
    expect(parseCreateRunRequest(value)).toEqual({ skillId: "verified-ai-radar", task: "do it", idempotencyKey: "550e8400-e29b-41d4-a716-446655440000" });
  });

  it("rejects non-JSON, cross-origin, malformed, and unknown fields", async () => {
    await expect(validateJsonWrite(request("{}", { "content-type": "text/plain" }), [])).rejects.toMatchObject({ status: 415 });
    await expect(validateJsonWrite(request("{}", { "content-type": "application/json", origin: "https://evil.test" }), [])).rejects.toMatchObject({ status: 403 });
    await expect(validateJsonWrite(request("{"), [])).rejects.toMatchObject({ status: 400 });
    await expect(validateJsonWrite(request('{"model":"x"}'), [])).rejects.toMatchObject({ status: 400 });
  });

  it("enforces task and UUID bounds", () => {
    const base = { skillId: "verified-ai-radar", idempotencyKey: "550e8400-e29b-41d4-a716-446655440000" };
    expect(() => parseCreateRunRequest({ ...base, task: "ab" })).toThrow();
    expect(() => parseCreateRunRequest({ ...base, task: "x".repeat(4001) })).toThrow();
    expect(() => parseCreateRunRequest({ ...base, task: "valid", idempotencyKey: "not-uuid" })).toThrow();
  });

  it("accepts only once and deny approval decisions", () => {
    expect(parseApprovalRequest({ decision: "once" })).toBe("once"); expect(parseApprovalRequest({ decision: "deny" })).toBe("deny");
    for (const decision of ["session", "always", "yolo", "approve"]) expect(() => parseApprovalRequest({ decision })).toThrow();
  });
});
