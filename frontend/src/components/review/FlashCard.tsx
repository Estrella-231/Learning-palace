'use client';

import { useState } from 'react';
import type { ReviewCard } from '@/types';
import { MarkdownContent } from '@/components/common/MarkdownContent';

interface FlashCardProps {
  card: ReviewCard;
  onRate: (rating: 'again' | 'hard' | 'good' | 'easy') => void;
  disabled?: boolean;
}

const RATING_OPTIONS = [
  { key: 'again' as const, label: '完全不会', color: 'bg-red-500 hover:bg-red-600' },
  { key: 'hard' as const, label: '困难', color: 'bg-orange-500 hover:bg-orange-600' },
  { key: 'good' as const, label: '良好', color: 'bg-emerald-500 hover:bg-emerald-600' },
  { key: 'easy' as const, label: '简单', color: 'bg-blue-500 hover:bg-blue-600' },
];

const CARD_TYPE_LABELS: Record<string, string> = {
  basic: '基础概念',
  contrast: '对比理解',
  application: '应用场景',
};

export function FlashCard({ card, onRate, disabled = false }: FlashCardProps) {
  const [flipped, setFlipped] = useState(false);

  return (
    <div className="w-full max-w-lg">
      {/* Card type badge */}
      <div className="text-center mb-3">
        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">
          {CARD_TYPE_LABELS[card.card_type] || card.card_type}
        </span>
      </div>

      {/* Card */}
      <div
        role="button"
        tabIndex={0}
        onClick={() => setFlipped(!flipped)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setFlipped(!flipped);
          }
        }}
        className={`w-full min-h-[250px] rounded-2xl border-2 cursor-pointer transition-all duration-300 flex items-center justify-center p-8 focus:outline-none focus:ring-2 focus:ring-primary-300 ${
          flipped
            ? 'border-emerald-300 bg-emerald-50'
            : 'border-gray-200 bg-white hover:border-primary-200'
        }`}
      >
        <div className="text-center">
          {!flipped ? (
            <>
              <p className="text-xs text-gray-400 mb-4">点击翻转查看答案</p>
              <div className="text-lg font-medium text-gray-800 leading-relaxed">
                <MarkdownContent>{card.question}</MarkdownContent>
              </div>
            </>
          ) : (
            <>
              <p className="text-xs text-emerald-500 mb-4">答案</p>
              <div className="text-lg text-gray-700 leading-relaxed">
                <MarkdownContent>{card.answer}</MarkdownContent>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Rating buttons (only show after flip) */}
      {flipped && (
        <div className="mt-4 grid grid-cols-4 gap-2">
          {RATING_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              onClick={(e) => {
                e.stopPropagation();
                onRate(opt.key);
                setFlipped(false);
              }}
              disabled={disabled}
              className={`px-3 py-2.5 text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${opt.color}`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
