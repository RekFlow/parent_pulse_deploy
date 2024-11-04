"use client";

import { useState } from "react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { ScrollArea } from "./components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "./components/ui/avatar";

interface Message {
  id: number;
  content: string;
  isUser: boolean;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content:
        "Welcome to the School Information System! You can ask about past events, grades, or upcoming events. How can I assist you today?",
      isUser: false,
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!inputMessage.trim()) return;

    const newUserMessage = {
      id: messages.length + 1,
      content: inputMessage,
      isUser: true,
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setInputMessage("");

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
      };
      setMessages((prev) => [...prev, newAIMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        id: messages.length + 2,
        content:
          "Sorry, there was an error processing your request. Please try again.",
        isUser: false,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <h1 className="text-4xl font-bold text-center text-purple-600 mb-8">
        School Information System
      </h1>

      <ScrollArea className="flex-grow mb-4 p-4 border rounded-lg">
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
                  <AvatarFallback>{message.isUser ? "U" : "AI"}</AvatarFallback>
                </Avatar>
                <div
                  className={`rounded-lg p-3 ${
                    message.isUser
                      ? "bg-purple-600 text-white"
                      : "bg-gray-100 dark:bg-gray-800"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      <form onSubmit={handleSubmit} className="flex space-x-2">
        <Input
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask about past events, grades, or upcoming events..."
          className="flex-grow"
        />
        <Button type="submit">Send</Button>
      </form>
    </div>
  );
}
