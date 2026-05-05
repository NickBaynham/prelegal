import Link from "next/link";
import { notFound } from "next/navigation";
import { getDocument, listVersions } from "@/lib/repo";

export const dynamic = "force-dynamic";

export default async function VersionsPage(
  props: PageProps<"/documents/[id]/versions">,
) {
  const { id } = await props.params;
  const doc = getDocument(id);
  if (!doc) notFound();
  const versions = listVersions(id);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Versions of “{doc.title}”</h1>
        <Link
          href={`/documents/${id}`}
          className="text-sm text-zinc-600 hover:text-zinc-900"
        >
          ← Back to latest
        </Link>
      </div>
      <ul className="divide-y divide-zinc-200 rounded-lg border border-zinc-200 bg-white">
        {versions.map((v, idx) => (
          <li key={v.id} className="flex items-center justify-between p-4">
            <div>
              <p className="font-medium">
                Version {v.version_number}
                {idx === 0 && (
                  <span className="ml-2 rounded bg-green-100 px-2 py-0.5 text-xs text-green-800">
                    current
                  </span>
                )}
              </p>
              <p className="text-sm text-zinc-500">
                Created {new Date(v.created_at).toLocaleString()}
              </p>
            </div>
            <Link
              href={`/documents/${id}/versions/${v.id}`}
              className="text-sm text-zinc-600 hover:text-zinc-900"
            >
              View →
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
