"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { HermesEnvelope, HermesPublicError } from "@/lib/hermes/types";

export type HermesResourceState<T> = {
  data: T | null;
  error: HermesPublicError | null;
  loading: boolean;
  refreshing: boolean;
  lastSuccessAt: string | null;
  refresh: () => Promise<void>;
};

async function browserFetch<T>(url: string, init: RequestInit): Promise<HermesEnvelope<T>> {
  const response = await fetch(url, { ...init, cache: "no-store" });
  return response.json() as Promise<HermesEnvelope<T>>;
}

export function useHermesResource<T>(url: string, intervalMs: number, fetcher: (url: string, init: RequestInit) => Promise<unknown> = browserFetch): HermesResourceState<T> {
  const [state, setState] = useState<Omit<HermesResourceState<T>, "refresh">>({ data: null, error: null, loading: true, refreshing: false, lastSuccessAt: null });
  const active = useRef<AbortController | null>(null);
  const generation = useRef(0);

  const run = useCallback(async (replace = false) => {
    if (active.current && !replace) return;
    if (replace) active.current?.abort();
    const controller = new AbortController();
    active.current = controller;
    const requestGeneration = ++generation.current;
    setState((current) => ({ ...current, refreshing: current.data !== null }));
    try {
      const envelope = await fetcher(url, { method: "GET", signal: controller.signal }) as HermesEnvelope<T>;
      if (controller.signal.aborted || requestGeneration !== generation.current) return;
      setState((current) => envelope.data !== null
        ? { data: envelope.data, error: envelope.error, loading: false, refreshing: false, lastSuccessAt: envelope.refreshedAt ?? current.lastSuccessAt }
        : { ...current, error: envelope.error, loading: false, refreshing: false });
    } catch {
      if (!controller.signal.aborted && requestGeneration === generation.current) setState((current) => ({ ...current, error: { code: "offline", message: "Hermes is unavailable." }, loading: false, refreshing: false }));
    } finally {
      if (active.current === controller) active.current = null;
    }
  }, [fetcher, url]);

  useEffect(() => {
    void run();
    const interval = window.setInterval(() => { void run(); }, intervalMs);
    return () => { window.clearInterval(interval); generation.current += 1; active.current?.abort(); active.current = null; };
  }, [intervalMs, run]);

  const refresh = useCallback(() => run(true), [run]);
  return { ...state, refresh };
}
