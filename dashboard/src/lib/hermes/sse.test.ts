import { describe, expect, it, vi } from "vitest";
import { createSanitizedSseStream } from "./sse";

const decode = async (stream: ReadableStream<Uint8Array>) => { const reader = stream.getReader(); const decoder = new TextDecoder(); let text = ""; for (;;) { const { done, value } = await reader.read(); if (done) return text; text += decoder.decode(value, { stream: true }); } };

describe("sanitized Hermes SSE", () => {
  it("normalizes split known frames and never relays raw fields", async () => {
    const encoder = new TextEncoder(); const upstream = new ReadableStream<Uint8Array>({ start(controller) { controller.enqueue(encoder.encode('data: {"event":"response.output_text.')); controller.enqueue(encoder.encode('delta","delta":"safe","authorization":"secret"}\n\n')); controller.close(); } });
    const output = await decode(createSanitizedSseStream(upstream));
    expect(output).toContain('"type":"output_delta"'); expect(output).toContain('"text":"safe"'); expect(output).not.toContain("authorization"); expect(output).not.toContain("secret");
  });

  it("converts unknown events to generic progress", async () => {
    const upstream = new ReadableStream<Uint8Array>({ start(controller) { controller.enqueue(new TextEncoder().encode('data: {"event":"future.event","payload":"hidden"}\n\n')); controller.close(); } });
    expect(await decode(createSanitizedSseStream(upstream))).toBe('data: {"type":"progress","label":"Hermes reported progress."}\n\n');
  });

  it("cancels the upstream stream when the browser cancels", async () => {
    const cancelled = vi.fn(); const upstream = new ReadableStream<Uint8Array>({ pull() {}, cancel: cancelled }); const reader = createSanitizedSseStream(upstream).getReader(); await reader.cancel(); expect(cancelled).toHaveBeenCalledOnce();
  });
});
