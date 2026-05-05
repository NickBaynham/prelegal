import { notFound } from "next/navigation";
import EditNdaClient from "@/components/EditNdaClient";
import { getDocument, getLatestVersion, parseVersionData } from "@/lib/repo";

export const dynamic = "force-dynamic";

export default async function EditDocumentPage(
  props: PageProps<"/documents/[id]/edit">,
) {
  const { id } = await props.params;
  const doc = getDocument(id);
  const latest = doc ? getLatestVersion(id) : undefined;
  if (!doc || !latest) notFound();

  const defaults = parseVersionData(latest);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Edit “{doc.title}”</h1>
      <p className="text-sm text-zinc-500">
        Saving creates a new version that supersedes the current one. Previous versions
        remain accessible from the version history.
      </p>
      <EditNdaClient id={id} defaults={defaults} />
    </div>
  );
}
