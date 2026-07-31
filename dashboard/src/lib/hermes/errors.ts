import type { HermesPublicError } from "./types";

export class HermesRequestError extends Error {
  constructor(public readonly kind: "auth" | "timeout" | "http" | "malformed", public readonly status?: number, message = "Hermes request failed") {
    super(message);
    this.name = "HermesRequestError";
  }
}

export function toPublicHermesError(error: unknown): HermesPublicError {
  if (error instanceof HermesRequestError && (error.kind === "auth" || error.status === 401 || error.status === 403)) return { code: "authentication", message: "Hermes authentication failed." };
  if ((error instanceof HermesRequestError && error.kind === "timeout") || error instanceof TypeError) return { code: "offline", message: "Hermes is unavailable." };
  return { code: "unavailable", message: "Hermes data is unavailable." };
}
