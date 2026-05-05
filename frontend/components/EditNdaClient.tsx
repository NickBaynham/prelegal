"use client";

import NdaForm from "@/components/NdaForm";
import { updateNdaAction } from "@/lib/actions";
import type { NdaFormValues } from "@/lib/schema";

export default function EditNdaClient({
  id,
  defaults,
}: {
  id: string;
  defaults: NdaFormValues;
}) {
  const onSubmit = async (values: NdaFormValues) => updateNdaAction(id, values);
  return <NdaForm submitLabel="Save as new version" onSubmit={onSubmit} defaultValues={defaults} />;
}
