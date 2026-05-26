'use client';

import { User, Bot } from 'lucide-react';
import { MarkdownContent } from '@/components/common/MarkdownContent';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
          isUser ? 'bg-primary-600 text-white' : 'bg-gradient-to-br from-blue-100 to-purple-100 text-blue-600'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      <div
        className={`max-w-[78%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'bg-primary-600 text-white rounded-tr-md shadow-sm'
            : 'bg-white border border-gray-100 text-gray-700 rounded-tl-md shadow-sm'
        }`}
      >
        {isUser ? message.content : (
          <MarkdownContent>{message.content}</MarkdownContent>
        )}
      </div>
    </div>
  );
}
