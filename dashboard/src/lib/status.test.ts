import { describe, expect, it } from "vitest";
import { formatStatus, statusTone } from "./status";

describe("status presentation", () => {
  it("formats machine statuses for people", () => expect(formatStatus("waiting-for-approval")).toBe("Waiting for approval"));
  it("uses distinct tones for failure and completion", () => expect(statusTone("failed")).not.toBe(statusTone("completed")));
});
