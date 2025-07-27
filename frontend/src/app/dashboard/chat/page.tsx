"use client";

import { useState, useRef, useEffect, useTransition } from "react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, CornerDownLeft, Loader } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import ReactMarkdown from 'react-markdown';

type Message = {
  role: "user" | "bot";
  content: string;
};

const mockFinancialData = JSON.stringify({
    netWorth: 120530,
    monthlySavings: 2500,
    goals: [
        { name: 'House Down Payment', progress: 0.60 },
        { name: 'Dream Vacation to Japan', progress: 0.35 },
    ],
    spending: [
        { category: "Groceries", amount: 450.75 },
        { category: "Utilities", amount: 220.50 },
        { category: "Dining Out", amount: 350.00 },
        { category: "Shopping", amount: 500.25 },
        { category: "Transport", amount: 150.00 },
    ]
}, null, 2);

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isPending, startTransition] = useTransition();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    startTransition(async () => {
      try {
        // Call backend /query endpoint with user_id, session_id, and query
        const payload = {
          user_id: "5555555555", // Replace with dynamic user_id if needed
          session_id: undefined, // Add session_id if available
          query: input,
        };
        const response = await fetch("http://localhost:8000/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error("API error");
        const result = await response.json();
        const botMessage: Message = { role: "bot", content: result.response };
        setMessages((prev) => [...prev, botMessage]);
      } catch (error) {
        console.error("API Error:", error);
        const errorMessage: Message = {
          role: "bot",
          content: "Sorry, I'm having trouble connecting. Please try again later.",
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    });
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
        setTimeout(() => {
            scrollAreaRef.current?.scrollTo({
                top: scrollAreaRef.current.scrollHeight,
                behavior: "smooth",
            });
        }, 100);
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <Card className="flex-1 flex flex-col">
        <CardContent className="flex-1 flex flex-col p-4">
          <ScrollArea className="flex-1" ref={scrollAreaRef}>
            <div className="space-y-4 pr-4">
              <div className="flex items-start gap-3">
                <Avatar className="h-8 w-8 border">
                  <AvatarFallback className="bg-accent text-accent-foreground">
                    <Bot size={18} />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-muted rounded-lg p-3 max-w-[85%]">
                  <p className="text-sm">
                    Hello! I'm your Hum-Safar Assistant. Ask me anything about your finances.
                  </p>
                </div>
              </div>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-3 ${
                    message.role === "user" ? "justify-end" : ""
                  }`}
                >
                  {message.role === "bot" && (
                    <Avatar className="h-8 w-8 border">
                      <AvatarFallback className="bg-accent text-accent-foreground">
                        <Bot size={18} />
                      </AvatarFallback>
                    </Avatar>
                  )}
                  <div
                    className={`rounded-lg p-3 max-w-[85%] ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {message.role === "bot" ? (
                      <div className="text-sm"><ReactMarkdown>{message.content}</ReactMarkdown></div>
                    ) : (
                      <p className="text-sm">{message.content}</p>
                    )}
                  </div>
                  {message.role === "user" && (
                    <Avatar className="h-8 w-8 border">
                      <AvatarFallback>
                        <User size={18} />
                      </AvatarFallback>
                    </Avatar>
                  )}
                </div>
              ))}
              {isPending && (
                <div className="flex items-start gap-3">
                  <Avatar className="h-8 w-8 border">
                    <AvatarFallback className="bg-accent text-accent-foreground">
                      <Bot size={18} />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-muted rounded-lg p-3 flex items-center space-x-2">
                    <Loader className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-muted-foreground">Thinking...</span>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
          <div className="mt-4">
            <form onSubmit={handleSendMessage} className="relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your finances..."
                className="pr-12"
                disabled={isPending}
              />
              <Button
                type="submit"
                size="icon"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8"
                variant="ghost"
                disabled={!input.trim() || isPending}
              >
                <CornerDownLeft className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}