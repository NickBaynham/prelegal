// HTTP client for the FastAPI backend.
//
// The base URL flips based on execution context: browser code uses
// NEXT_PUBLIC_API_URL (publicly reachable), server-side code (server
// components, server actions, API routes) prefers INTERNAL_API_URL so it
// can reach the backend over Docker's internal network.

const browserBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const serverBase =
  process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function baseUrl(): string {
  return typeof window === "undefined" ? serverBase : browserBase;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export function isNotFound(err: unknown): boolean {
  return err instanceof ApiError && err.status === 404;
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${baseUrl()}${path}`;
  const res = await fetch(url, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(res.status, body || res.statusText);
  }
  return (await res.json()) as T;
}
