import { cleanup, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "./LoginForm";

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  localStorage.clear();
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("LoginForm API integration", () => {
  it("sends credentials and stores the access token on success", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ access_token: "session-token", token_type: "bearer" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<LoginForm onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText("E-mail"), "person@example.com");
    await user.type(screen.getByLabelText("Senha"), "correct-horse-battery");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/auth/login",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ email: "person@example.com", password: "correct-horse-battery" }),
      }),
    );
    const requestHeaders = fetchMock.mock.calls[0][1]?.headers as Headers;
    expect(requestHeaders.get("Content-Type")).toBe("application/json");
    expect(localStorage.getItem("dataflow_access_token")).toBe("session-token");
    expect(onSuccess).toHaveBeenCalledOnce();
  });

  it("shows the API error and clears an expired token on unauthorized response", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    localStorage.setItem("dataflow_access_token", "expired-token");
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ detail: "Invalid credentials" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );

    render(<LoginForm onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText("E-mail"), "person@example.com");
    await user.type(screen.getByLabelText("Senha"), "wrong-password");
    await user.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid credentials");
    expect(localStorage.getItem("dataflow_access_token")).toBeNull();
    expect(onSuccess).not.toHaveBeenCalled();
  });
});