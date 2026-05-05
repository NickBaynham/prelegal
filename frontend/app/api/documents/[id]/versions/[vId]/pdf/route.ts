import { NextResponse } from "next/server";
import { getDocument, getVersion } from "@/lib/repo";
import { renderPdf } from "@/lib/pdf";

export const dynamic = "force-dynamic";

export async function GET(
  _req: Request,
  ctx: RouteContext<"/api/documents/[id]/versions/[vId]/pdf">,
) {
  const { id, vId } = await ctx.params;
  const doc = getDocument(id);
  const version = doc ? getVersion(id, vId) : undefined;
  if (!doc || !version) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  let pdf: Buffer;
  try {
    pdf = await renderPdf({
      title: doc.title,
      versionNumber: version.version_number,
      markdown: version.rendered_markdown,
    });
  } catch (err) {
    console.error("PDF generation failed", err);
    return NextResponse.json({ error: "PDF generation failed" }, { status: 500 });
  }

  const filename = sanitizeFilename(`${doc.title}-v${version.version_number}.pdf`);
  return new NextResponse(new Uint8Array(pdf), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  });
}

function sanitizeFilename(name: string): string {
  return name.replace(/[^a-zA-Z0-9._-]+/g, "_");
}
