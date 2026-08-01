import { openHermesRunEvents } from "@/lib/hermes/run-client";
import { isValidRunId } from "@/lib/hermes/run-normalize";
import { runFailure } from "@/lib/hermes/run-route";
import { createSanitizedSseStream } from "@/lib/hermes/sse";

export async function GET(request: Request, context: { params: Promise<{ runId: string }> }) {
  try {
    const { runId } = await context.params; if (!isValidRunId(runId)) return Response.json({ data: null, error: { code: "unavailable", message: "Invalid run ID." }, refreshedAt: null }, { status: 400 });
    const controller = new AbortController(); const abort = () => controller.abort(); request.signal.addEventListener("abort", abort, { once: true });
    const upstream = await openHermesRunEvents(runId, { signal: controller.signal });
    return new Response(createSanitizedSseStream(upstream.body!, () => controller.abort()), { headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", "X-Accel-Buffering": "no", Connection: "keep-alive" } });
  } catch (error) { return runFailure(error); }
}
