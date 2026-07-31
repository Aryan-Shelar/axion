import { toPublicHermesError } from "./errors";
import { hermesGet } from "./client";
import type { HermesEnvelope, HermesPath } from "./types";

export function successResponse<T>(data: T): Response {
  return Response.json({ data, error: null, refreshedAt: new Date().toISOString() } satisfies HermesEnvelope<T>);
}

export function failureResponse(error: unknown): Response {
  const safe = toPublicHermesError(error);
  return Response.json({ data: null, error: safe, refreshedAt: null } satisfies HermesEnvelope<never>, { status: safe.code === "authentication" ? 401 : 503 });
}

export async function handleHermesRoute<T>(path: HermesPath, normalize: (value: unknown) => T, request: typeof hermesGet = hermesGet): Promise<Response> {
  try { return successResponse(normalize(await request(path))); } catch (error) { return failureResponse(error); }
}
