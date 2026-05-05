"use client";

import { useForm, useWatch, type SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { ndaSchema, type NdaFormValues } from "@/lib/schema";

type Props = {
  defaultValues?: Partial<NdaFormValues>;
  submitLabel: string;
  onSubmit: (values: NdaFormValues) => Promise<{ error: string } | void>;
};

const blankParty = { printName: "", title: "", company: "", noticeAddress: "", signedDate: "" };

const baseDefaults: NdaFormValues = {
  title: "",
  purpose: "Evaluating whether to enter into a business relationship with the other party.",
  effectiveDate: new Date().toISOString().slice(0, 10),
  mndaTerm: { type: "expires", years: 1 },
  termOfConfidentiality: { type: "years", years: 1 },
  governingLaw: "",
  jurisdiction: "",
  modifications: "",
  parties: [blankParty, blankParty],
};

function mergeDefaults(partial?: Partial<NdaFormValues>): NdaFormValues {
  if (!partial) return baseDefaults;
  return {
    ...baseDefaults,
    ...partial,
    parties: [
      { ...blankParty, ...(partial.parties?.[0] ?? {}) },
      { ...blankParty, ...(partial.parties?.[1] ?? {}) },
    ],
  };
}

export default function NdaForm({ defaultValues, submitLabel, onSubmit }: Props) {
  const form = useForm<NdaFormValues>({
    resolver: zodResolver(ndaSchema),
    defaultValues: mergeDefaults(defaultValues),
  });
  const [submitError, setSubmitError] = useState<string | null>(null);
  const { register, handleSubmit, control, formState } = form;
  const mndaTermType = useWatch({ control, name: "mndaTerm.type" });
  const tocType = useWatch({ control, name: "termOfConfidentiality.type" });

  const submit: SubmitHandler<NdaFormValues> = async (values) => {
    setSubmitError(null);
    const result = await onSubmit(values);
    if (result && "error" in result) setSubmitError(result.error);
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-8">
      <Section title="Document">
        <Field label="Title" error={formState.errors.title?.message}>
          <input
            {...register("title")}
            placeholder="e.g. Acme ⇄ Globex MNDA"
            className="input"
          />
        </Field>
      </Section>

      <Section title="Purpose">
        <Field
          label="How Confidential Information may be used"
          error={formState.errors.purpose?.message}
        >
          <textarea {...register("purpose")} rows={3} className="input" />
        </Field>
      </Section>

      <Section title="Effective Date">
        <Field label="Date" error={formState.errors.effectiveDate?.message}>
          <input type="date" {...register("effectiveDate")} className="input" />
        </Field>
      </Section>

      <Section title="MNDA Term">
        <fieldset className="space-y-2">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="expires"
              {...register("mndaTerm.type")}
            />
            Expires
            <input
              type="number"
              min={1}
              {...register("mndaTerm.years", { valueAsNumber: true })}
              disabled={mndaTermType !== "expires"}
              className="input w-20"
            />
            year(s) from Effective Date
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="continues"
              {...register("mndaTerm.type")}
            />
            Continues until terminated
          </label>
        </fieldset>
      </Section>

      <Section title="Term of Confidentiality">
        <fieldset className="space-y-2">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="years"
              {...register("termOfConfidentiality.type")}
            />
            <input
              type="number"
              min={1}
              {...register("termOfConfidentiality.years", { valueAsNumber: true })}
              disabled={tocType !== "years"}
              className="input w-20"
            />
            year(s) from Effective Date
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="perpetuity"
              {...register("termOfConfidentiality.type")}
            />
            In perpetuity
          </label>
        </fieldset>
      </Section>

      <Section title="Governing Law & Jurisdiction">
        <Field label="Governing Law (state)" error={formState.errors.governingLaw?.message}>
          <input {...register("governingLaw")} placeholder="e.g. Delaware" className="input" />
        </Field>
        <Field
          label="Jurisdiction (city/county and state)"
          error={formState.errors.jurisdiction?.message}
        >
          <input
            {...register("jurisdiction")}
            placeholder="e.g. New Castle, DE"
            className="input"
          />
        </Field>
      </Section>

      <Section title="MNDA Modifications">
        <Field label="Optional — list any modifications to the Standard Terms">
          <textarea {...register("modifications")} rows={3} className="input" />
        </Field>
      </Section>

      {([0, 1] as const).map((index) => (
        <Section key={index} title={`Party ${index + 1}`}>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field
              label="Print Name"
              error={formState.errors.parties?.[index]?.printName?.message}
            >
              <input
                {...register(`parties.${index}.printName` as const)}
                className="input"
              />
            </Field>
            <Field
              label="Title"
              error={formState.errors.parties?.[index]?.title?.message}
            >
              <input
                {...register(`parties.${index}.title` as const)}
                className="input"
              />
            </Field>
            <Field
              label="Company"
              error={formState.errors.parties?.[index]?.company?.message}
            >
              <input
                {...register(`parties.${index}.company` as const)}
                className="input"
              />
            </Field>
            <Field
              label="Notice Address (email or postal)"
              error={formState.errors.parties?.[index]?.noticeAddress?.message}
            >
              <input
                {...register(`parties.${index}.noticeAddress` as const)}
                className="input"
              />
            </Field>
            <Field label="Signed Date (optional)">
              <input
                type="date"
                {...register(`parties.${index}.signedDate` as const)}
                className="input"
              />
            </Field>
          </div>
        </Section>
      ))}

      {submitError && (
        <p className="rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {submitError}
        </p>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={formState.isSubmitting}
          className="rounded bg-zinc-900 px-5 py-2 text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {formState.isSubmitting ? "Saving…" : submitLabel}
        </button>
      </div>
    </form>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-zinc-200 p-5">
      <h2 className="mb-4 text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-zinc-700">{label}</span>
      {children}
      {error && <span className="block text-sm text-red-600">{error}</span>}
    </label>
  );
}
