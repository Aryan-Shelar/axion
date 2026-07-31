import { describe, expect, it } from "vitest";
import { HermesRequestError, toPublicHermesError } from "./errors";

describe("Hermes error mapping", () => {
  it.each([401, 403])("maps HTTP %s to authentication without upstream detail", (status) => {
    expect(toPublicHermesError(new HermesRequestError("auth", status, "upstream secret"))).toEqual({ code: "authentication", message: "Hermes authentication failed." });
  });

  it("maps timeout and connection failures to offline", () => {
    expect(toPublicHermesError(new HermesRequestError("timeout"))).toEqual({ code: "offline", message: "Hermes is unavailable." });
    expect(toPublicHermesError(new TypeError("fetch failed C:/private"))).toEqual({ code: "offline", message: "Hermes is unavailable." });
  });

  it("maps malformed responses to a safe unavailable error", () => {
    expect(toPublicHermesError(new HermesRequestError("malformed"))).toEqual({ code: "unavailable", message: "Hermes data is unavailable." });
  });
});
