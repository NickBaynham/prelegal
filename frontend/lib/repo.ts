// Document repository — thin async wrapper over the FastAPI backend.
// Function names mirror the prior SQLite-backed module so callers keep
// the same shape, with `await` added.

import { ApiError, isNotFound, request } from "./api";
import type { NdaFormValues } from "./schema";

export type DocumentRow = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type VersionRow = {
  id: string;
  document_id: string;
  version_number: number;
  data: NdaFormValues;
  rendered_markdown: string;
  created_at: string;
};

export type DocumentSummary = DocumentRow & {
  latest_version_number: number;
  latest_version_id: string;
};

export type DocumentDetail = {
  document: DocumentRow;
  latest_version: VersionRow;
};

type CreateDocumentResponse = {
  id: string;
  latest_version_id: string;
  latest_version_number: number;
};

type CreateVersionResponse = {
  version_id: string;
  version_number: number;
};

async function maybe<T>(promise: Promise<T>): Promise<T | undefined> {
  try {
    return await promise;
  } catch (err) {
    if (isNotFound(err)) return undefined;
    throw err;
  }
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  return request<DocumentSummary[]>("/documents");
}

export async function getDocumentDetail(id: string): Promise<DocumentDetail | undefined> {
  return maybe(request<DocumentDetail>(`/documents/${encodeURIComponent(id)}`));
}

export async function getDocument(id: string): Promise<DocumentRow | undefined> {
  const detail = await getDocumentDetail(id);
  return detail?.document;
}

export async function getLatestVersion(id: string): Promise<VersionRow | undefined> {
  const detail = await getDocumentDetail(id);
  return detail?.latest_version;
}

export async function listVersions(id: string): Promise<VersionRow[]> {
  return request<VersionRow[]>(`/documents/${encodeURIComponent(id)}/versions`);
}

export async function getVersion(id: string, versionId: string): Promise<VersionRow | undefined> {
  return maybe(
    request<VersionRow>(
      `/documents/${encodeURIComponent(id)}/versions/${encodeURIComponent(versionId)}`,
    ),
  );
}

export async function createDocument(values: NdaFormValues): Promise<CreateDocumentResponse> {
  return request<CreateDocumentResponse>("/documents", {
    method: "POST",
    body: JSON.stringify(values),
  });
}

export async function addVersion(
  id: string,
  values: NdaFormValues,
): Promise<CreateVersionResponse> {
  return request<CreateVersionResponse>(`/documents/${encodeURIComponent(id)}/versions`, {
    method: "POST",
    body: JSON.stringify(values),
  });
}

export { ApiError };
