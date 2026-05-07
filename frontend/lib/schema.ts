import { z } from "zod";

const partySchema = z.object({
  printName: z.string().trim().min(1, "Required"),
  title: z.string().trim().min(1, "Required"),
  company: z.string().trim().min(1, "Required"),
  noticeAddress: z.string().trim().min(1, "Required"),
  signedDate: z.string().trim().optional().or(z.literal("")),
});

const mndaTermSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("expires"), years: z.number().int().min(1).max(50) }),
  z.object({ type: z.literal("continues") }),
]);

const termOfConfidentialitySchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("years"), years: z.number().int().min(1).max(99) }),
  z.object({ type: z.literal("perpetuity") }),
]);

export const ndaSchema = z.object({
  title: z.string().trim().min(1, "Required").max(200),
  purpose: z.string().trim().min(1, "Required"),
  effectiveDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD"),
  mndaTerm: mndaTermSchema,
  termOfConfidentiality: termOfConfidentialitySchema,
  governingLaw: z.string().trim().min(1, "Required"),
  jurisdiction: z.string().trim().min(1, "Required"),
  modifications: z.string(),
  parties: z.tuple([partySchema, partySchema]),
});

export type NdaFormValues = z.infer<typeof ndaSchema>;
export type Party = z.infer<typeof partySchema>;
