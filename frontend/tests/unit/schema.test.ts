import { describe, expect, it } from "vitest";
import { ndaSchema } from "@/lib/schema";

const validValues = {
  title: "ACME × Globex Mutual NDA",
  purpose: "Evaluate a partnership.",
  effectiveDate: "2026-05-06",
  mndaTerm: { type: "expires" as const, years: 2 },
  termOfConfidentiality: { type: "perpetuity" as const },
  governingLaw: "Delaware",
  jurisdiction: "Delaware",
  modifications: "",
  parties: [
    {
      printName: "Alice",
      title: "CEO",
      company: "ACME",
      noticeAddress: "1 Way",
      signedDate: "",
    },
    {
      printName: "Bob",
      title: "CTO",
      company: "Globex",
      noticeAddress: "2 Ave",
      signedDate: "",
    },
  ],
} as const;

describe("ndaSchema", () => {
  it("accepts a valid form payload", () => {
    expect(ndaSchema.safeParse(validValues).success).toBe(true);
  });

  it("rejects effectiveDate that is not YYYY-MM-DD", () => {
    const result = ndaSchema.safeParse({ ...validValues, effectiveDate: "2026/05/06" });
    expect(result.success).toBe(false);
  });

  it("rejects expires term with years out of range", () => {
    const result = ndaSchema.safeParse({
      ...validValues,
      mndaTerm: { type: "expires", years: 99 },
    });
    expect(result.success).toBe(false);
  });

  it("requires a non-empty title", () => {
    const result = ndaSchema.safeParse({ ...validValues, title: "  " });
    expect(result.success).toBe(false);
  });
});
