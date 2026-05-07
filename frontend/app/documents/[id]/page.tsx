import Link from "next/link";
import { notFound } from "next/navigation";
import NdaDocument from "@/components/NdaDocument";
import DocumentActions from "@/components/DocumentActions";
import { getDocumentDetail } from "@/lib/repo";

export const dynamic = "force-dynamic";

export default async function DocumentPage(props: PageProps<"/documents/[id]">) {
  const { id } = await props.params;
  const detail = await getDocumentDetail(id);
  if (!detail) notFound();
  const { document: doc, latest_version: latest } = detail;

  return (
    <div className="space-y-6">
      <div className="no-print flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{doc.title}</h1>
          <p className="text-sm text-zinc-500">
            Version {latest.version_number} · created{" "}
            {new Date(latest.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <Link
            href={`/documents/${doc.id}/edit`}
            className="rounded border border-zinc-300 px-3 py-1.5 hover:bg-zinc-50"
          >
            Edit (creates new version)
          </Link>
          <Link
            href={`/documents/${doc.id}/versions`}
            className="rounded border border-zinc-300 px-3 py-1.5 hover:bg-zinc-50"
          >
            All versions
          </Link>
          <DocumentActions
            documentId={doc.id}
            versionId={latest.id}
            versionNumber={latest.version_number}
            title={doc.title}
          />
        </div>
      </div>
      <div className="rounded-lg border border-zinc-200 bg-white p-10 shadow-sm">
        <NdaDocument markdown={latest.rendered_markdown} />
      </div>
    </div>
  );
}
