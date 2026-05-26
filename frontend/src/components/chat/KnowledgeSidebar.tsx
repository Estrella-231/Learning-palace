'use client';

import { useChatStore } from '@/stores/chatStore';
import { useRouter } from 'next/navigation';
import { Lightbulb, Link2, StickyNote } from 'lucide-react';
import { MarkdownContent } from '@/components/common/MarkdownContent';

const TYPE_COLORS: Record<string, string> = {
  concept: 'bg-blue-50 text-blue-700 border-blue-200',
  example: 'bg-green-50 text-green-700 border-green-200',
  misconception: 'bg-red-50 text-red-700 border-red-200',
  question: 'bg-yellow-50 text-yellow-700 border-yellow-200',
};

const TYPE_LABELS: Record<string, string> = {
  concept: '概念',
  example: '例子',
  misconception: '误区',
  question: '问题',
};

export function KnowledgeSidebar() {
  const nodes = useChatStore((s) => s.knowledgeNodes);
  const edges = useChatStore((s) => s.knowledgeEdges);
  const cards = useChatStore((s) => s.reviewCards);
  const router = useRouter();

  if (nodes.length === 0 && edges.length === 0 && cards.length === 0) {
    return (
      <div className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-6 h-6 rounded-lg bg-gray-100 flex items-center justify-center">
            <Lightbulb className="w-3.5 h-3.5 text-gray-400" />
          </div>
          <h2 className="text-sm font-semibold text-gray-500">知识提取</h2>
        </div>
        <div className="text-center mt-16">
          <div className="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center mx-auto mb-3">
            <Lightbulb className="w-6 h-6 text-gray-300" />
          </div>
          <p className="text-xs text-gray-400 max-w-[180px] mx-auto leading-relaxed">
            开始提问后，这里会实时展示从 AI 回答中提取的知识节点、关系和复习卡片
          </p>
        </div>
      </div>
    );
  }

  const count = nodes.length + edges.length + cards.length;

  return (
    <div className="p-4 space-y-5">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-lg bg-amber-100 flex items-center justify-center">
          <Lightbulb className="w-3.5 h-3.5 text-amber-600" />
        </div>
        <h2 className="text-sm font-semibold text-gray-600">知识提取</h2>
        <span className="text-[10px] text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full tabular-nums">
          {count}
        </span>
      </div>

      {/* New Nodes */}
      {nodes.length > 0 && (
        <div>
          <h3 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">
            知识点 ({nodes.length})
          </h3>
          <div className="space-y-1.5">
            {nodes.map((node) => (
              <button
                key={node.id}
                onClick={() => router.push(`/node/${node.id}`)}
                className={`w-full text-left px-3 py-2 rounded-lg border text-xs transition-all hover:shadow-sm hover:-translate-y-0.5 ${TYPE_COLORS[node.type] || TYPE_COLORS.concept}`}
              >
                <div className="font-semibold mb-0.5">{node.title}</div>
                <div className="text-[10px] opacity-60 line-clamp-2 markdown-inline">
                  <MarkdownContent>{node.summary}</MarkdownContent>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* New Edges */}
      {edges.length > 0 && (
        <div>
          <h3 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">
            关系 ({edges.length})
          </h3>
          <div className="space-y-1">
            {edges.map((edge) => (
              <div
                key={edge.id}
                className="px-3 py-1.5 text-xs bg-indigo-50 text-indigo-700 rounded-lg border border-indigo-100"
              >
                <span className="font-medium">{edge.relation_type}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* New Review Cards */}
      {cards.length > 0 && (
        <div>
          <h3 className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">
            复习卡片 ({cards.length})
          </h3>
          <div className="space-y-1.5">
            {cards.map((card) => (
              <div
                key={card.id}
                className="px-3 py-2 bg-emerald-50 text-emerald-800 rounded-lg border border-emerald-100 text-xs"
              >
                <div className="font-medium leading-relaxed">
                  <MarkdownContent>{card.question}</MarkdownContent>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
