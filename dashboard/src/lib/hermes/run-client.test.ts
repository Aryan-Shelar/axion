import { afterEach, describe, expect, it, vi } from "vitest";
import { createHermesRun, getHermesRun, openHermesRunEvents, respondHermesApproval, stopHermesRun } from "./run-client";

afterEach(() => { delete process.env.HERMES_API_URL; delete process.env.HERMES_API_KEY; });
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

describe("restricted Hermes run client", () => {
  it("constructs the documented create request and forwards idempotency", async () => {
    process.env.HERMES_API_URL = "http://127.0.0.1:8642/"; process.env.HERMES_API_KEY = "server-secret";
    const fetchImpl = vi.fn(async () => json({ run_id: "run_1", status: "started" })) as unknown as typeof fetch;
    await createHermesRun({ input: "task", instructions: "controlled", sessionId: "axion_1", idempotencyKey: "550e8400-e29b-41d4-a716-446655440000" }, { fetchImpl });
    const [url, init] = (fetchImpl as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(url).toBe("http://127.0.0.1:8642/v1/runs"); expect(init.method).toBe("POST"); expect(init.cache).toBe("no-store");
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer server-secret"); expect(new Headers(init.headers).get("idempotency-key")).toBe("550e8400-e29b-41d4-a716-446655440000");
    expect(JSON.parse(init.body)).toEqual({ input: "task", instructions: "controlled", session_id: "axion_1" });
  });

  it("uses only fixed run operations and rejects unsafe IDs", async () => {
    const fetchImpl = vi.fn(async () => json({ run_id: "run_1", status: "running" })) as unknown as typeof fetch;
    await getHermesRun("run_1", { fetchImpl }); await respondHermesApproval("run_1", "deny", { fetchImpl }); await stopHermesRun("run_1", { fetchImpl });
    expect((fetchImpl as ReturnType<typeof vi.fn>).mock.calls.map(([url, init]) => [url, init.method])).toEqual([["http://127.0.0.1:8642/v1/runs/run_1", "GET"], ["http://127.0.0.1:8642/v1/runs/run_1/approval", "POST"], ["http://127.0.0.1:8642/v1/runs/run_1/stop", "POST"]]);
    expect(JSON.parse((fetchImpl as ReturnType<typeof vi.fn>).mock.calls[1][1].body)).toEqual({ choice: "deny" });
    await expect(getHermesRun("../secret", { fetchImpl })).rejects.toThrow("Invalid run ID");
  });

  it("returns the live event response without buffering it", async () => {
    const stream = new ReadableStream({ start(controller) { controller.enqueue(new TextEncoder().encode("data: {}\n\n")); } });
    const fetchImpl = vi.fn(async () => new Response(stream, { headers: { "content-type": "text/event-stream" } })) as unknown as typeof fetch;
    const response = await openHermesRunEvents("run_1", { fetchImpl }); expect(response.body).toBe(stream);
  });
});
