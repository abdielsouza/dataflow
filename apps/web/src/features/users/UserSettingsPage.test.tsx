import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { UserSettingsPage } from "./UserSettingsPage";

const fetchMock = vi.fn<typeof fetch>();
const userProfile = {
  id: "user-1",
  username: "person",
  email: "person@example.com",
};

function renderSettings(onAccountDeleted = vi.fn()) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return {
    onAccountDeleted,
    ...render(
      <QueryClientProvider client={queryClient}>
        <UserSettingsPage
          user={userProfile}
          isLoading={false}
          error={null}
          onAccountDeleted={onAccountDeleted}
        />
      </QueryClientProvider>,
    ),
  };
}

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem("dataflow_access_token", "session-token");
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("UserSettingsPage API integration", () => {
  it("updates the current user's profile", async () => {
    const user = userEvent.setup();
    renderSettings();
    await user.clear(screen.getByLabelText("Nome de usuário"));
    await user.type(screen.getByLabelText("Nome de usuário"), "updated-person");
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({ ...userProfile, username: "updated-person" }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await user.click(screen.getByRole("button", { name: "Salvar alterações" }));

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/users/me",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ username: "updated-person" }),
      }),
    );
    expect(await screen.findByRole("status")).toHaveTextContent("atualizados");
  });

  it("deletes the current user's account after confirmation", async () => {
    const user = userEvent.setup();
    const onAccountDeleted = vi.fn();
    renderSettings(onAccountDeleted);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));

    await user.click(screen.getByRole("button", { name: "Excluir minha conta" }));

    expect(window.confirm).toHaveBeenCalledOnce();
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/users/me",
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(onAccountDeleted).toHaveBeenCalledOnce();
  });
});
