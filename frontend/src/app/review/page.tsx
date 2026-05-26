'use client';

import { useEffect, useState, useCallback } from 'react';
import { FlashCard } from '@/components/review/FlashCard';
import { ReviewProgress } from '@/components/review/ReviewProgress';
import { useCourseStore } from '@/stores/courseStore';
import { getDueCards, getReviewStats, submitReview } from '@/lib/api';
import type { ReviewCard, ReviewStats } from '@/types';
import { RefreshCw, PartyPopper, AlertCircle } from 'lucide-react';

export default function ReviewPage() {
  const selectedCourseId = useCourseStore((s) => s.selectedCourseId);
  const courses = useCourseStore((s) => s.courses);

  const [cards, setCards] = useState<ReviewCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [dueCards, reviewStats] = await Promise.all([
        getDueCards(selectedCourseId || undefined),
        getReviewStats(selectedCourseId || undefined),
      ]);
      setCards(dueCards);
      setCurrentIndex(0);
      setStats(reviewStats);
      setFinished(dueCards.length === 0);
    } catch (err) {
      console.error('Failed to load review data:', err);
      setError('加载失败，请重试');
    } finally {
      setLoading(false);
    }
  }, [selectedCourseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRate = async (rating: 'again' | 'hard' | 'good' | 'easy') => {
    const card = cards[currentIndex];
    if (!card || submitting) return;

    setSubmitting(true);
    setError(null);
    try {
      await submitReview(card.id, rating);

      if (currentIndex + 1 >= cards.length) {
        setFinished(true);
        const reviewStats = await getReviewStats(selectedCourseId || undefined);
        setStats(reviewStats);
      } else {
        setCurrentIndex((i) => i + 1);
      }
    } catch (err) {
      console.error('Review submission failed:', err);
      setError('提交失败，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  if (!selectedCourseId && courses.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <p>请先在左侧创建课程</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-lg font-bold text-gray-800">复习中心</h1>
        {stats && (
          <span className="text-xs text-gray-400">
            {stats.due_cards} 张待复习 / 共 {stats.total_cards} 张
          </span>
        )}
      </div>

      {/* Progress */}
      {stats && <ReviewProgress stats={stats} current={currentIndex} total={cards.length} />}

      {/* Card area */}
      <div className="flex-1 flex items-center justify-center py-8">
        {loading ? (
          <p className="text-gray-400">加载中...</p>
        ) : finished ? (
          <div className="text-center space-y-4">
            <PartyPopper className="w-10 h-10 text-amber-500 mx-auto" />
            <h2 className="text-xl font-semibold text-gray-700">本轮复习完成！</h2>
            <p className="text-sm text-gray-400">
              已复习 {cards.length} 张卡片，继续保持！
            </p>
            <button
              onClick={loadData}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700"
            >
              <RefreshCw className="w-4 h-4" />
              刷新检查新卡片
            </button>
          </div>
        ) : cards[currentIndex] ? (
          <div className="w-full max-w-lg space-y-3">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}
            <FlashCard card={cards[currentIndex]} onRate={handleRate} disabled={submitting} />
          </div>
        ) : (
          <div className="text-center text-gray-400">
            <p className="text-lg mb-2">暂无待复习卡片</p>
            <p className="text-sm">
              开始学习对话后，系统会自动生成复习卡片并安排复习时间
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
