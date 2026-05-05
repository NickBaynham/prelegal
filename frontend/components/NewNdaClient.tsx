"use client";

import NdaForm from "@/components/NdaForm";
import { createNdaAction } from "@/lib/actions";

export default function NewNdaClient() {
  return <NdaForm submitLabel="Create document" onSubmit={createNdaAction} />;
}
