import ChatNdaClient from "@/components/ChatNdaClient";

export default function NewDocumentPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">New Mutual NDA</h1>
      <ChatNdaClient />
    </div>
  );
}
