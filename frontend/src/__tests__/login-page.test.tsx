// @vitest-environment happy-dom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoginClient } from "@/app/(auth)/login/_components/LoginClient";
import { QueryClientProviderWrapper } from "@/components/query-client-provider";
import { server } from "@/test/msw-server";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    replace,
    push: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

function renderLogin() {
  return render(
    <QueryClientProviderWrapper>
      <LoginClient />
    </QueryClientProviderWrapper>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.history.replaceState({}, "", "http://localhost:3000/login");
  });

  afterEach(() => {
    cleanup();
  });

  it("submits corp_id and event_code to the login API", async () => {
    let body: unknown;
    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/auth/login"),
        async ({ request }) => {
          body = await request.json();
          return HttpResponse.json({ ok: true });
        },
      ),
    );

    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/corp id/i), "alice");
    await user.type(screen.getByLabelText(/event code/i), "event-99");
    await user.click(screen.getByRole("button", { name: /sign in$/i }));

    await waitFor(() => {
      expect(body).toEqual({ corp_id: "alice", event_code: "event-99" });
    });
    await waitFor(() => {
      expect(replace).toHaveBeenCalledWith("/lobby");
    });
  });

  it("shows an error message on 401 from the login API", async () => {
    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/auth/login"),
        () => HttpResponse.json({ message: "Invalid event code" }, { status: 401 }),
      ),
    );

    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/corp id/i), "x");
    await user.type(screen.getByLabelText(/event code/i), "y");
    await user.click(screen.getByRole("button", { name: /sign in$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid corp ID or event code");
    expect(replace).not.toHaveBeenCalled();
  });

  it("disables submit while the login request is in flight", async () => {
    let release!: () => void;
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });

    server.use(
      http.post(
        ({ request }) => new URL(request.url).pathname.endsWith("/api/auth/login"),
        async () => {
          await gate;
          return HttpResponse.json({ ok: true });
        },
      ),
    );

    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText(/corp id/i), "a");
    await user.type(screen.getByLabelText(/event code/i), "b");
    await user.click(screen.getByRole("button", { name: /sign in$/i }));

    expect(screen.getByRole("button", { name: /signing in/i })).toBeDisabled();

    release();
    await waitFor(() => {
      expect(replace).toHaveBeenCalled();
    });
  });
});
