'use client';

import { ChatPanel } from '@/components/chat/ChatPanel';
import { KnowledgeSidebar } from '@/components/chat/KnowledgeSidebar';

export default function ChatPage() {
  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col min-w-0">
        <ChatPanel />
      </div>
      <div className="w-80 border-l border-gray-200 bg-white overflow-y-auto shrink-0">
        <KnowledgeSidebar />
      </div>
    </div>
  );
}
