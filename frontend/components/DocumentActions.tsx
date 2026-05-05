"use client";

import { useEffect, useState } from "react";

type Props = {
  documentId: string;
  versionId: string;
  versionNumber: number;
  title: string;
};

export default function DocumentActions({
  documentId,
  versionId,
  versionNumber,
  title,
}: Props) {
  const [origin, setOrigin] = useState<string>("");

  useEffect(() => {
    setOrigin(window.location.origin);
  }, []);

  const pdfHref = `/api/documents/${documentId}/versions/${versionId}/pdf`;
  const shareUrl = origin
    ? `${origin}/documents/${documentId}/versions/${versionId}`
    : "";
  const subject = `NDA: ${title} (v${versionNumber})`;
  const body = `Mutual NDA "${title}" — version ${versionNumber}.\n\nView: ${shareUrl}\n`;
  const mailtoHref = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

  return (
    <>
      <a
        href={pdfHref}
        className="rounded border border-zinc-300 bg-white px-3 py-1.5 hover:bg-zinc-50"
      >
        Download PDF
      </a>
      <a
        href={mailtoHref}
        className="rounded border border-zinc-300 bg-white px-3 py-1.5 hover:bg-zinc-50"
      >
        Email
      </a>
      <button
        type="button"
        onClick={() => window.print()}
        className="rounded border border-zinc-300 bg-white px-3 py-1.5 hover:bg-zinc-50"
      >
        Print
      </button>
    </>
  );
}
