"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2 } from "lucide-react";

interface Message {
  id: number;
  content: string;
  isUser: boolean;
  timestamp: number;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
    setMessages([
      {
        id: 1,
        content:
          "Welcome to the School Information System! You can ask about past events, grades, or upcoming events. How can I assist you today?",
        isUser: false,
        timestamp: Date.now(),
      },
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const newUserMessage = {
      id: messages.length + 1,
      content: inputMessage,
      isUser: true,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: inputMessage }),
      });

      const data = await response.json();

      const aiResponse =
        data.response ||
        data.error ||
        "Sorry, I couldn't process that request.";

      const newAIMessage = {
        id: messages.length + 2,
        content: aiResponse,
        isUser: false,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, newAIMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        id: messages.length + 2,
        content:
          "Sorry, there was an error processing your request. Please try again.",
        isUser: false,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        id: 1,
        content:
          "Welcome to the School Information System! You can ask about past events, grades, or upcoming events. How can I assist you today?",
        isUser: false,
        timestamp: Date.now(),
      },
    ]);
  };

  const formatTimestamp = (timestamp: number) => {
    if (!mounted) return "";
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <h1 className="text-4xl font-bold text-center text-purple-600 mb-8">
        School Information System
      </h1>

      <div className="flex-grow mb-4 border rounded-lg overflow-hidden">
        <div className="h-[calc(100vh-250px)] overflow-y-auto p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.isUser ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex items-start space-x-2 max-w-[80%] ${
                    message.isUser ? "flex-row-reverse space-x-reverse" : ""
                  }`}
                >
                  <Avatar>
                    <AvatarFallback>
                      {message.isUser ? "U" : "AI"}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <div
                      className={`rounded-lg p-3 ${
                        message.isUser
                          ? "bg-purple-600 text-white"
                          : "bg-gray-100 dark:bg-gray-800"
                      }`}
                    >
                      {message.content}
                    </div>
                    <span className="text-xs text-gray-500 mt-1">
                      {formatTimestamp(message.timestamp)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex space-x-2">
        <Input
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask about past events, grades, or upcoming events..."
          className="flex-grow"
          disabled={isLoading}
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Sending
            </>
          ) : (
            "Send"
          )}
        </Button>
        <Button type="button" onClick={clearConversation}>
          Clear
        </Button>
      </form>
    </div>
  );
}
