import type { UseFormReturn } from "react-hook-form";
import { request } from "./api";
import type { NdaFormValues, Party } from "./schema";

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  role: ChatRole;
  content: string;
};

export type PartialParty = Partial<Party>;

export type PartialNdaFormValues = {
  title?: string | null;
  purpose?: string | null;
  effectiveDate?: string | null;
  mndaTerm?: NdaFormValues["mndaTerm"] | null;
  termOfConfidentiality?: NdaFormValues["termOfConfidentiality"] | null;
  governingLaw?: string | null;
  jurisdiction?: string | null;
  modifications?: string | null;
  party1?: PartialParty | null;
  party2?: PartialParty | null;
};

export type ChatRequest = {
  messages: ChatMessage[];
  currentValues: PartialNdaFormValues;
};

export type ChatResponse = {
  assistantMessage: string;
  extractedValues: PartialNdaFormValues;
};

const SET_OPTS = { shouldValidate: false, shouldDirty: true } as const;

export async function assistChat(body: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function snapshotCurrentValues(values: NdaFormValues): PartialNdaFormValues {
  return {
    title: values.title || null,
    purpose: values.purpose || null,
    effectiveDate: values.effectiveDate || null,
    mndaTerm: values.mndaTerm,
    termOfConfidentiality: values.termOfConfidentiality,
    governingLaw: values.governingLaw || null,
    jurisdiction: values.jurisdiction || null,
    modifications: values.modifications || null,
    party1: values.parties?.[0] ?? null,
    party2: values.parties?.[1] ?? null,
  };
}

/**
 * Push AI-extracted fields into the form. Skips null/undefined so the AI can
 * only ever fill blanks; user edits are never overwritten with null.
 *
 * Discriminated unions are written field-by-field (`mndaTerm.type` then
 * `mndaTerm.years`) rather than as a single parent setValue, because the
 * radios in NdaForm are uncontrolled — RHF only updates the DOM when the
 * leaf-registered path is touched.
 */
export function applyExtractedValues(
  form: UseFormReturn<NdaFormValues>,
  extracted: PartialNdaFormValues,
): void {
  if (extracted.title != null) form.setValue("title", extracted.title, SET_OPTS);
  if (extracted.purpose != null) form.setValue("purpose", extracted.purpose, SET_OPTS);
  if (extracted.effectiveDate != null)
    form.setValue("effectiveDate", extracted.effectiveDate, SET_OPTS);
  if (extracted.mndaTerm != null) applyMndaTerm(form, extracted.mndaTerm);
  if (extracted.termOfConfidentiality != null)
    applyTermOfConfidentiality(form, extracted.termOfConfidentiality);
  if (extracted.governingLaw != null)
    form.setValue("governingLaw", extracted.governingLaw, SET_OPTS);
  if (extracted.jurisdiction != null)
    form.setValue("jurisdiction", extracted.jurisdiction, SET_OPTS);
  if (extracted.modifications != null)
    form.setValue("modifications", extracted.modifications, SET_OPTS);

  applyParty(form, 0, extracted.party1);
  applyParty(form, 1, extracted.party2);
}

function applyMndaTerm(
  form: UseFormReturn<NdaFormValues>,
  term: NonNullable<PartialNdaFormValues["mndaTerm"]>,
): void {
  form.setValue("mndaTerm.type", term.type, SET_OPTS);
  if (term.type === "expires") {
    form.setValue("mndaTerm.years", term.years, SET_OPTS);
  }
}

function applyTermOfConfidentiality(
  form: UseFormReturn<NdaFormValues>,
  term: NonNullable<PartialNdaFormValues["termOfConfidentiality"]>,
): void {
  form.setValue("termOfConfidentiality.type", term.type, SET_OPTS);
  if (term.type === "years") {
    form.setValue("termOfConfidentiality.years", term.years, SET_OPTS);
  }
}

function applyParty(
  form: UseFormReturn<NdaFormValues>,
  index: 0 | 1,
  party: PartialParty | null | undefined,
): void {
  if (!party) return;
  if (party.printName != null)
    form.setValue(`parties.${index}.printName`, party.printName, SET_OPTS);
  if (party.title != null) form.setValue(`parties.${index}.title`, party.title, SET_OPTS);
  if (party.company != null)
    form.setValue(`parties.${index}.company`, party.company, SET_OPTS);
  if (party.noticeAddress != null)
    form.setValue(`parties.${index}.noticeAddress`, party.noticeAddress, SET_OPTS);
  if (party.signedDate != null)
    form.setValue(`parties.${index}.signedDate`, party.signedDate, SET_OPTS);
}
