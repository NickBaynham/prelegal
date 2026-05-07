"use client";

import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "@/lib/chat";

type Props = {
  greeting: string;
  messages: ChatMessage[];
  onSend: (text: string) => void | Promise<void>;
  isBusy: boolean;
  unavailable?: boolean;
};

export default function ChatPanel({ greeting, messages, onSend, isBusy, unavailable }: Props) {
  const [draft, setDraft] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages.length, isBusy]);

  const disabled = isBusy || unavailable;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || disabled) return;
    setDraft("");
    await onSend(text);
  }

  return (
    <section className="flex h-[calc(100vh-12rem)] min-h-[28rem] flex-col rounded-lg border border-zinc-200 bg-white">
      <header className="border-b border-zinc-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-zinc-700">AI Assistant</h2>
        <p className="text-xs text-zinc-500">
          Tell me about the agreement and I&rsquo;ll fill in the form on the right.
        </p>
      </header>

      {unavailable && (
        <div
          role="alert"
          className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber-800"
        >
          AI assistant is unavailable. You can still fill in the form directly.
        </div>
      )}

      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        <Bubble message={{ role: "assistant", content: greeting }} />
        {messages.map((m, i) => (
          <Bubble key={i} message={m} />
        ))}
        {isBusy && <Bubble message={{ role: "assistant", content: "…" }} />}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-zinc-200 p-3">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              (e.currentTarget.form as HTMLFormElement | null)?.requestSubmit();
            }
          }}
          rows={2}
          placeholder={unavailable ? "AI unavailable" : "Type a message…"}
          disabled={disabled}
          className="input flex-1 resize-none disabled:bg-zinc-50 disabled:text-zinc-400"
          aria-label="Message"
        />
        <button
          type="submit"
          disabled={disabled || !draft.trim()}
          className="self-end rounded bg-zinc-900 px-4 py-2 text-sm text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </section>
  );
}

function Bubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
          isUser ? "bg-zinc-900 text-white" : "bg-zinc-100 text-zinc-900"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
