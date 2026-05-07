import { describe, expect, it } from "vitest";
import { ApiError, isNotFound } from "@/lib/api";

describe("ApiError", () => {
  it("preserves status and message", () => {
    const err = new ApiError(404, "missing");
    expect(err.status).toBe(404);
    expect(err.message).toBe("missing");
    expect(err.name).toBe("ApiError");
  });
});

describe("isNotFound", () => {
  it("returns true only for ApiError with status 404", () => {
    expect(isNotFound(new ApiError(404, "x"))).toBe(true);
    expect(isNotFound(new ApiError(500, "x"))).toBe(false);
    expect(isNotFound(new Error("not an api error"))).toBe(false);
    expect(isNotFound(null)).toBe(false);
    expect(isNotFound(undefined)).toBe(false);
  });
});
