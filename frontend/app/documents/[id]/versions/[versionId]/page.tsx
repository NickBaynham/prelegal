import Link from "next/link";
import { notFound } from "next/navigation";
import NdaDocument from "@/components/NdaDocument";
import DocumentActions from "@/components/DocumentActions";
import { getDocument, getVersion } from "@/lib/repo";

export const dynamic = "force-dynamic";

export default async function VersionPage(
  props: PageProps<"/documents/[id]/versions/[versionId]">,
) {
  const { id, versionId } = await props.params;
  const doc = await getDocument(id);
  const version = doc ? await getVersion(id, versionId) : undefined;
  if (!doc || !version) notFound();

  return (
    <div className="space-y-6">
      <div className="no-print flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{doc.title}</h1>
          <p className="text-sm text-zinc-500">
            Version {version.version_number} (historical) · created{" "}
            {new Date(version.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <Link
            href={`/documents/${doc.id}/versions`}
            className="rounded border border-zinc-300 px-3 py-1.5 hover:bg-zinc-50"
          >
            All versions
          </Link>
          <DocumentActions
            documentId={doc.id}
            versionId={version.id}
            versionNumber={version.version_number}
            title={doc.title}
          />
        </div>
      </div>
      <div className="rounded-lg border border-zinc-200 bg-white p-10 shadow-sm">
        <NdaDocument markdown={version.rendered_markdown} />
      </div>
    </div>
  );
}
