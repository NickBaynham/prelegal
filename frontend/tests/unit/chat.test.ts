import { describe, expect, it, vi } from "vitest";
import type { UseFormReturn } from "react-hook-form";
import { applyExtractedValues, snapshotCurrentValues } from "@/lib/chat";
import type { NdaFormValues } from "@/lib/schema";

function makeFakeForm() {
  const setValue = vi.fn();
  return {
    form: { setValue } as unknown as UseFormReturn<NdaFormValues>,
    setValue,
  };
}

const baseParty = {
  printName: "",
  title: "",
  company: "",
  noticeAddress: "",
  signedDate: "",
};

const baseValues: NdaFormValues = {
  title: "",
  purpose: "",
  effectiveDate: "2026-05-07",
  mndaTerm: { type: "expires", years: 1 },
  termOfConfidentiality: { type: "years", years: 1 },
  governingLaw: "",
  jurisdiction: "",
  modifications: "",
  parties: [baseParty, baseParty],
};

describe("applyExtractedValues", () => {
  it("sets only fields that are present and non-null", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, {
      title: "Draft",
      governingLaw: "Delaware",
      purpose: null,
    });
    expect(setValue).toHaveBeenCalledWith("title", "Draft", expect.any(Object));
    expect(setValue).toHaveBeenCalledWith("governingLaw", "Delaware", expect.any(Object));
    expect(setValue).not.toHaveBeenCalledWith("purpose", expect.anything(), expect.anything());
  });

  it("maps party1/party2 to parties.0 / parties.1", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, {
      party1: { company: "ACME", printName: "Alice" },
      party2: { company: "Globex" },
    });
    expect(setValue).toHaveBeenCalledWith("parties.0.company", "ACME", expect.any(Object));
    expect(setValue).toHaveBeenCalledWith("parties.0.printName", "Alice", expect.any(Object));
    expect(setValue).toHaveBeenCalledWith("parties.1.company", "Globex", expect.any(Object));
    expect(setValue).not.toHaveBeenCalledWith(
      "parties.1.printName",
      expect.anything(),
      expect.anything(),
    );
  });

  it("skips parties that are null or undefined", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, { party1: null });
    expect(setValue).not.toHaveBeenCalled();
  });

  it("never overwrites with null (so user edits are preserved)", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, {
      title: null,
      purpose: null,
      mndaTerm: null,
      party1: null,
    });
    expect(setValue).not.toHaveBeenCalled();
  });

  it("passes shouldValidate:false so chat fills don't trigger noisy validation", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, { title: "Hi" });
    expect(setValue).toHaveBeenCalledWith(
      "title",
      "Hi",
      expect.objectContaining({ shouldValidate: false }),
    );
  });

  it("writes mndaTerm via leaf paths so radios update visually", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, { mndaTerm: { type: "expires", years: 3 } });
    expect(setValue).toHaveBeenCalledWith("mndaTerm.type", "expires", expect.any(Object));
    expect(setValue).toHaveBeenCalledWith("mndaTerm.years", 3, expect.any(Object));
    expect(setValue).not.toHaveBeenCalledWith(
      "mndaTerm",
      expect.anything(),
      expect.anything(),
    );
  });

  it("does not write a years leaf when mndaTerm.type is 'continues'", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, { mndaTerm: { type: "continues" } });
    expect(setValue).toHaveBeenCalledWith("mndaTerm.type", "continues", expect.any(Object));
    expect(setValue).not.toHaveBeenCalledWith(
      "mndaTerm.years",
      expect.anything(),
      expect.anything(),
    );
  });

  it("writes termOfConfidentiality via leaf paths", () => {
    const { form, setValue } = makeFakeForm();
    applyExtractedValues(form, { termOfConfidentiality: { type: "perpetuity" } });
    expect(setValue).toHaveBeenCalledWith(
      "termOfConfidentiality.type",
      "perpetuity",
      expect.any(Object),
    );
    expect(setValue).not.toHaveBeenCalledWith(
      "termOfConfidentiality",
      expect.anything(),
      expect.anything(),
    );
  });
});

describe("snapshotCurrentValues", () => {
  it("flattens parties[0..1] to party1/party2", () => {
    const snapshot = snapshotCurrentValues({
      ...baseValues,
      title: "Draft",
      parties: [
        { ...baseParty, company: "ACME" },
        { ...baseParty, company: "Globex" },
      ],
    });
    expect(snapshot.title).toBe("Draft");
    expect(snapshot.party1?.company).toBe("ACME");
    expect(snapshot.party2?.company).toBe("Globex");
  });

  it("returns null for empty string fields so the LLM doesn't see noise", () => {
    const snapshot = snapshotCurrentValues(baseValues);
    expect(snapshot.title).toBeNull();
    expect(snapshot.governingLaw).toBeNull();
  });

  it("preserves discriminated unions verbatim", () => {
    const snapshot = snapshotCurrentValues({
      ...baseValues,
      mndaTerm: { type: "continues" },
      termOfConfidentiality: { type: "perpetuity" },
    });
    expect(snapshot.mndaTerm).toEqual({ type: "continues" });
    expect(snapshot.termOfConfidentiality).toEqual({ type: "perpetuity" });
  });
});
