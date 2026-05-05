import Link from "next/link";
import { listDocuments } from "@/lib/repo";

export const dynamic = "force-dynamic";

export default function Home() {
  const documents = listDocuments();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Documents</h1>
        <Link
          href="/new"
          className="rounded bg-zinc-900 px-4 py-2 text-sm text-white hover:bg-zinc-700"
        >
          New NDA
        </Link>
      </div>

      {documents.length === 0 ? (
        <div className="rounded-lg border border-dashed border-zinc-300 bg-white p-10 text-center text-zinc-600">
          <p>No documents yet.</p>
          <Link href="/new" className="mt-3 inline-block text-zinc-900 underline">
            Create your first Mutual NDA →
          </Link>
        </div>
      ) : (
        <ul className="divide-y divide-zinc-200 rounded-lg border border-zinc-200 bg-white">
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center justify-between p-4">
              <div>
                <Link
                  href={`/documents/${doc.id}`}
                  className="font-medium text-zinc-900 hover:underline"
                >
                  {doc.title}
                </Link>
                <p className="text-sm text-zinc-500">
                  v{doc.latest_version_number} · updated{" "}
                  {new Date(doc.updated_at).toLocaleString()}
                </p>
              </div>
              <div className="flex gap-3 text-sm">
                <Link
                  href={`/documents/${doc.id}/versions`}
                  className="text-zinc-600 hover:text-zinc-900"
                >
                  Versions
                </Link>
                <Link
                  href={`/documents/${doc.id}/edit`}
                  className="text-zinc-600 hover:text-zinc-900"
                >
                  Edit
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
