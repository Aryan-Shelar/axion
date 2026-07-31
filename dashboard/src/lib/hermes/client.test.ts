import { afterEach, describe, expect, it, vi } from "vitest";
import { hermesGet } from "./client";

afterEach(() => { vi.useRealTimers(); delete process.env.HERMES_API_URL; delete process.env.HERMES_API_KEY; });

describe("hermesGet", () => {
  it("uses the local default, bearer auth, and no-store caching", async () => {
    process.env.HERMES_API_KEY = "private-key";
    const fetchImpl = vi.fn(async () => new Response(JSON.stringify({ status: "ok" }), { status: 200 }));
    await hermesGet("/health", { fetchImpl });
    const [url, init] = fetchImpl.mock.calls[0];
    expect(url).toBe("http://127.0.0.1:8642/health");
    expect(init.cache).toBe("no-store");
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer private-key");
  });

  it("maps a request that exceeds five seconds to timeout", async () => {
    vi.useFakeTimers();
    const fetchImpl = vi.fn((_url: string, init: RequestInit) => new Promise<Response>((_resolve, reject) => init.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")))));
    const request = hermesGet("/health", { fetchImpl: fetchImpl as typeof fetch });
    const assertion = expect(request).rejects.toMatchObject({ kind: "timeout" });
    await vi.advanceTimersByTimeAsync(5001);
    await assertion;
  });

  it.each([401, 403])("maps HTTP %s to an authentication error", async (status) => {
    const fetchImpl = vi.fn(async () => new Response("do not expose", { status }));
    await expect(hermesGet("/v1/skills", { fetchImpl })).rejects.toMatchObject({ kind: "auth", status });
  });

  it("rejects malformed JSON without exposing its body", async () => {
    const fetchImpl = vi.fn(async () => new Response("C:/private api_key=secret", { status: 200 }));
    await expect(hermesGet("/v1/models", { fetchImpl })).rejects.toMatchObject({ kind: "malformed", message: "Hermes returned invalid JSON" });
  });
});
