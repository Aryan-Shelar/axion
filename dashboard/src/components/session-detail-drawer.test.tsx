import React, { useRef, useState } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { HermesSessionSummary } from "@/lib/hermes/types";
import { SessionDetailDrawer } from "./session-detail-drawer";

const session: HermesSessionSummary = { id: "safe-id", title: "Research session", source: "desktop", status: "active", updatedAt: "2026-07-31T10:00:00Z" };

function Harness() {
  const [open, setOpen] = useState(false); const opener = useRef<HTMLButtonElement>(null);
  return <><button ref={opener} onClick={() => setOpen(true)}>Open session</button><SessionDetailDrawer session={open ? session : null} opener={opener.current} onClose={() => setOpen(false)} /></>;
}

describe("SessionDetailDrawer", () => {
  it("renders only approved metadata as an accessible dialog", () => {
    render(<SessionDetailDrawer session={session} opener={null} onClose={() => undefined} />);
    const dialog = screen.getByRole("dialog", { name: "Research session details" });
    expect(dialog).toHaveTextContent("safe-id"); expect(dialog).toHaveTextContent("desktop"); expect(dialog).toHaveTextContent("active"); expect(dialog).toHaveTextContent("Last updated");
    expect(screen.queryByText(/message|prompt|tool argument|output|secret/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /delete|edit|resume|stop|run/i })).not.toBeInTheDocument();
  });

  it("closes from the close button, backdrop, and Escape", () => {
    const onClose = vi.fn(); const { rerender } = render(<SessionDetailDrawer session={session} opener={null} onClose={onClose} />);
    fireEvent.click(screen.getByRole("button", { name: "Close session details" }));
    fireEvent.click(screen.getByRole("button", { name: "Close session drawer backdrop" }));
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalledTimes(3);
    rerender(<SessionDetailDrawer session={null} opener={null} onClose={onClose} />);
  });

  it("traps focus while open", async () => {
    render(<SessionDetailDrawer session={session} opener={null} onClose={() => undefined} />);
    const close = screen.getByRole("button", { name: "Close session details" });
    await waitFor(() => expect(close).toHaveFocus());
    fireEvent.keyDown(document, { key: "Tab" }); expect(close).toHaveFocus();
    fireEvent.keyDown(document, { key: "Tab", shiftKey: true }); expect(close).toHaveFocus();
  });

  it("restores focus to the row that opened it", async () => {
    render(<Harness />); const opener = screen.getByRole("button", { name: "Open session" });
    opener.focus(); fireEvent.click(opener);
    await waitFor(() => expect(screen.getByRole("button", { name: "Close session details" })).toHaveFocus());
    fireEvent.keyDown(document, { key: "Escape" });
    await waitFor(() => expect(opener).toHaveFocus());
  });
});
