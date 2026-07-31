import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useHermesResource } from "./use-hermes-resource";

afterEach(() => vi.useRealTimers());

describe("useHermesResource", () => {
  it("loads immediately and preserves the last success after a temporary failure", async () => {
    const fetcher = vi.fn().mockResolvedValueOnce({ data: { value: 4 }, error: null, refreshedAt: "2026-07-31T10:00:00Z" }).mockResolvedValueOnce({ data: null, error: { code: "offline", message: "Hermes is unavailable." }, refreshedAt: null });
    const { result } = renderHook(() => useHermesResource("/api/hermes/health", 15_000, fetcher));
    await waitFor(() => expect(result.current.data).toEqual({ value: 4 }));
    await act(() => result.current.refresh());
    expect(result.current.data).toEqual({ value: 4 });
    expect(result.current.error?.code).toBe("offline");
    expect(result.current.lastSuccessAt).toBe("2026-07-31T10:00:00Z");
  });

  it("aborts an in-flight request on unmount", () => {
    let signal: AbortSignal | undefined;
    const fetcher = vi.fn((_url: string, init: RequestInit) => { signal = init.signal ?? undefined; return new Promise(() => undefined); });
    const { unmount } = renderHook(() => useHermesResource("/api/hermes/health", 15_000, fetcher));
    unmount();
    expect(signal?.aborted).toBe(true);
  });

  it("cancels a stale request before manual refresh and ignores its result", async () => {
    const pending: Array<(value: unknown) => void> = [];
    const signals: AbortSignal[] = [];
    const fetcher = vi.fn((_url: string, init: RequestInit) => new Promise((resolve) => { pending.push(resolve); signals.push(init.signal as AbortSignal); }));
    const { result } = renderHook(() => useHermesResource<{ value: number }>("/api/hermes/health", 15_000, fetcher));
    act(() => { void result.current.refresh(); });
    expect(signals[0].aborted).toBe(true);
    await act(async () => pending[1]({ data: { value: 2 }, error: null, refreshedAt: "now" }));
    await act(async () => pending[0]({ data: { value: 1 }, error: null, refreshedAt: "old" }));
    expect(result.current.data).toEqual({ value: 2 });
  });
});
