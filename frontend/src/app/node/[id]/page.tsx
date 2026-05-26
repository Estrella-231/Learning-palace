'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, ExternalLink, AlertTriangle, Lightbulb, BookOpen } from 'lucide-react';
import { getNodeDetail } from '@/lib/api';
import type { NodeDetail } from '@/types';
import { MarkdownContent } from '@/components/common/MarkdownContent';

const TYPE_LABELS: Record<string, string> = {
  concept: '概念',
  example: '例子',
  misconception: '误区',
  question: '问题',
};

const RELATION_LABELS: Record<string, string> = {
  prerequisite_of: '前置知识',
  part_of: '组成部分',
  example_of: '示例',
  contrast_with: '对比',
  cause_of: '原因',
  used_for: '用途',
  improves: '改进',
  similar_to: '相似概念',
  contains: '包含',
};

export default function NodeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<NodeDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      getNodeDetail(id)
        .then(setDetail)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        加载中...
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        知识点不存在
      </div>
    );
  }

  const { node, source_message, related_nodes, edges, review_cards } = detail;

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto p-6 space-y-6">
        {/* Back */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="w-4 h-4" />
          返回
        </button>

        {/* Title + Meta */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
              {TYPE_LABELS[node.type] || node.type}
            </span>
            <span className="text-xs text-gray-400">
              掌握度 {Math.round(node.mastery * 100)}%
            </span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{node.title}</h1>
          <MarkdownContent className="mt-2 text-gray-600 leading-relaxed">{node.summary}</MarkdownContent>
        </div>

        {/* Content */}
        {node.content && (
          <div className="bg-gray-50 rounded-xl p-4">
            <h2 className="text-sm font-semibold text-gray-500 mb-2">知识点详情</h2>
            <MarkdownContent className="text-sm text-gray-700 leading-relaxed">
              {node.content}
            </MarkdownContent>
          </div>
        )}

        {/* Source message */}
        {source_message && (
          <div className="bg-blue-50 rounded-xl p-4">
            <div className="flex items-center gap-1.5 mb-2">
              <BookOpen className="w-3.5 h-3.5 text-blue-500" />
              <h2 className="text-sm font-semibold text-blue-600">来源对话</h2>
            </div>
            <MarkdownContent className="text-sm text-blue-800 line-clamp-6">
              {source_message.content}
            </MarkdownContent>
            <button
              onClick={() => router.push('/chat')}
              className="mt-2 text-xs text-blue-500 hover:text-blue-700 flex items-center gap-1"
            >
              查看完整对话 <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Related nodes */}
        {related_nodes.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-500 mb-3">相关知识点</h2>
            <div className="grid grid-cols-2 gap-2">
              {edges.map((edge, i) => {
                const relatedId =
                  edge.source_node_id === node.id
                    ? edge.target_node_id
                    : edge.source_node_id;
                const relatedNode = related_nodes.find((n) => n.id === relatedId);
                if (!relatedNode) return null;
                const relationType = RELATION_LABELS[edge.relation_type] || edge.relation_type;
                const isIncoming = edge.target_node_id === node.id;
                return (
                  <button
                    key={edge.id}
                    onClick={() => router.push(`/node/${relatedId}`)}
                    className="text-left p-3 rounded-lg border border-gray-200 hover:border-primary-200 hover:bg-primary-50/30 transition-colors"
                  >
                    <span className="text-[10px] text-gray-400">{relationType}</span>
                    <div className="text-sm font-medium text-gray-800 mt-0.5">
                      {isIncoming ? '← ' : '→ '}
                      {relatedNode.title}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Review cards */}
        {review_cards.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-gray-500 mb-3">复习卡片</h2>
            <div className="space-y-2">
              {review_cards.map((card) => (
                <div
                  key={card.id}
                  className="p-3 rounded-lg border border-emerald-200 bg-emerald-50"
                >
                  <div className="flex items-center gap-1.5 mb-1">
                    <Lightbulb className="w-3 h-3 text-emerald-500" />
                    <span className="text-xs text-emerald-600 font-medium">
                      {card.card_type === 'basic'
                        ? '基础概念'
                        : card.card_type === 'contrast'
                          ? '对比理解'
                          : '应用场景'}
                    </span>
                  </div>
                  <MarkdownContent className="text-sm font-medium text-emerald-900">{card.question}</MarkdownContent>
                  <MarkdownContent className="text-xs text-emerald-700 mt-1 opacity-70">{card.answer}</MarkdownContent>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Misconceptions */}
        {node.type === 'misconception' && (
          <div className="bg-red-50 rounded-xl p-4">
            <div className="flex items-center gap-1.5 mb-2">
              <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
              <h2 className="text-sm font-semibold text-red-600">常见误区</h2>
            </div>
            <MarkdownContent className="text-sm text-red-800">{node.content}</MarkdownContent>
          </div>
        )}
      </div>
    </div>
  );
}
