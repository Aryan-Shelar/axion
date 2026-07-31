import "server-only";
import { HermesRequestError } from "./errors";
import type { HermesPath } from "./types";

const DEFAULT_HERMES_URL = "http://127.0.0.1:8642";
const TIMEOUT_MS = 5_000;

export async function hermesGet(path: HermesPath, options: { signal?: AbortSignal; fetchImpl?: typeof fetch } = {}): Promise<unknown> {
  const controller = new AbortController();
  let timedOut = false;
  const onExternalAbort = () => controller.abort(options.signal?.reason);
  options.signal?.addEventListener("abort", onExternalAbort, { once: true });
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, TIMEOUT_MS);
  const baseUrl = (process.env.HERMES_API_URL || DEFAULT_HERMES_URL).replace(/\/+$/, "");
  const headers = new Headers({ accept: "application/json" });
  if (process.env.HERMES_API_KEY) headers.set("authorization", `Bearer ${process.env.HERMES_API_KEY}`);

  try {
    const response = await (options.fetchImpl ?? fetch)(`${baseUrl}${path}`, { method: "GET", headers, cache: "no-store", signal: controller.signal });
    if (response.status === 401 || response.status === 403) throw new HermesRequestError("auth", response.status);
    if (!response.ok) throw new HermesRequestError("http", response.status);
    try { return await response.json(); } catch { throw new HermesRequestError("malformed", response.status, "Hermes returned invalid JSON"); }
  } catch (error) {
    if (timedOut) throw new HermesRequestError("timeout");
    throw error;
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener("abort", onExternalAbort);
  }
}
