"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import ChatPanel from "@/components/ChatPanel";
import NdaForm from "@/components/NdaForm";
import { ApiError } from "@/lib/api";
import {
  applyExtractedValues,
  assistChat,
  snapshotCurrentValues,
  type ChatMessage,
} from "@/lib/chat";
import { createNdaAction } from "@/lib/actions";
import { baseDefaults, ndaSchema, type NdaFormValues } from "@/lib/schema";

const HISTORY_TURNS = 10;
const GREETING =
  "Hi — I can help you draft a Mutual NDA. Tell me anything you know about the parties or " +
  "the deal, or ask me a question about any field. You can also fill the form directly on the right.";

export default function ChatNdaClient() {
  const form = useForm<NdaFormValues>({
    resolver: zodResolver(ndaSchema),
    defaultValues: baseDefaults,
  });
  // `messages` is the LLM history — only real user/assistant turns. The greeting
  // is rendered separately and never sent to the model.
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [aiUnavailable, setAiUnavailable] = useState(false);

  async function handleSend(userText: string) {
    const userMessage: ChatMessage = { role: "user", content: userText };
    const nextHistory = [...messages, userMessage];
    setMessages(nextHistory);
    setIsBusy(true);
    try {
      const response = await assistChat({
        messages: nextHistory.slice(-HISTORY_TURNS),
        currentValues: snapshotCurrentValues(form.getValues()),
      });
      applyExtractedValues(form, response.extractedValues);
      setMessages([
        ...nextHistory,
        { role: "assistant", content: response.assistantMessage },
      ]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setAiUnavailable(true);
        setMessages([
          ...nextHistory,
          {
            role: "assistant",
            content: "I'm unavailable right now, but you can still fill the form directly.",
          },
        ]);
      } else {
        setMessages([
          ...nextHistory,
          {
            role: "assistant",
            content: "Something went wrong. Please try that again, or fill the form directly.",
          },
        ]);
      }
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
      <ChatPanel
        greeting={GREETING}
        messages={messages}
        onSend={handleSend}
        isBusy={isBusy}
        unavailable={aiUnavailable}
      />
      <NdaForm form={form} submitLabel="Create document" onSubmit={createNdaAction} />
    </div>
  );
}
