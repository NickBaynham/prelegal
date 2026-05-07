"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { addVersion, createDocument } from "./repo";
import { ndaSchema, type NdaFormValues } from "./schema";

export type ActionError = { error: string };

export async function createNdaAction(values: NdaFormValues): Promise<ActionError | never> {
  const parsed = ndaSchema.safeParse(values);
  if (!parsed.success) {
    return { error: parsed.error.issues.map((i) => i.message).join("; ") };
  }
  const { id } = await createDocument(parsed.data);
  revalidatePath("/");
  redirect(`/documents/${id}`);
}

export async function updateNdaAction(
  documentId: string,
  values: NdaFormValues,
): Promise<ActionError | never> {
  const parsed = ndaSchema.safeParse(values);
  if (!parsed.success) {
    return { error: parsed.error.issues.map((i) => i.message).join("; ") };
  }
  await addVersion(documentId, parsed.data);
  revalidatePath("/");
  revalidatePath(`/documents/${documentId}`);
  revalidatePath(`/documents/${documentId}/versions`);
  redirect(`/documents/${documentId}`);
}
