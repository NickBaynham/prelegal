import ReactMarkdown from "react-markdown";

export default function NdaDocument({ markdown }: { markdown: string }) {
  return (
    <article className="nda-document prose prose-zinc max-w-none">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </article>
  );
}
