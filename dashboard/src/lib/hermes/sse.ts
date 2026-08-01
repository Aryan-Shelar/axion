import { normalizeRunEvent } from "./run-normalize";

const encoder = new TextEncoder();

export function createSanitizedSseStream(upstream: ReadableStream<Uint8Array>, onCancel?: () => void): ReadableStream<Uint8Array> {
  const reader = upstream.getReader(); const decoder = new TextDecoder(); let buffer = ""; let cancelled = false;
  const emitFrames = (controller: ReadableStreamDefaultController<Uint8Array>, flush = false) => {
    const normalized = buffer.replace(/\r\n/g, "\n"); const frames = normalized.split("\n\n"); buffer = flush ? "" : frames.pop() ?? "";
    for (const frame of frames) for (const line of frame.split("\n")) if (line.startsWith("data:")) {
      try { const event = normalizeRunEvent(JSON.parse(line.slice(5).trim())); if (event) controller.enqueue(encoder.encode(`data: ${JSON.stringify(event)}\n\n`)); } catch { /* malformed upstream event is ignored */ }
    }
  };
  return new ReadableStream<Uint8Array>({
    async start(controller) { try { for (;;) { const { done, value } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); emitFrames(controller); } buffer += decoder.decode(); if (buffer.trim()) { buffer += "\n\n"; emitFrames(controller, true); } if (!cancelled) controller.close(); } catch (error) { if (!cancelled) controller.error(error); } },
    async cancel() { cancelled = true; onCancel?.(); await reader.cancel(); },
  });
}
