'use client';

import type { ReviewStats } from '@/types';

interface ReviewProgressProps {
  stats: ReviewStats;
  current: number;
  total: number;
}

export function ReviewProgress({ stats, current, total }: ReviewProgressProps) {
  const progress = total > 0 ? (current / total) * 100 : 0;

  return (
    <div className="space-y-2">
      {/* Progress bar */}
      {total > 0 && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-400">复习进度</span>
            <span className="text-xs text-gray-500">
              {current} / {total}
            </span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-3 gap-2">
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <div className="text-lg font-bold text-gray-800">{stats.total_cards}</div>
          <div className="text-[10px] text-gray-400">总卡片</div>
        </div>
        <div className="text-center p-2 bg-amber-50 rounded-lg">
          <div className="text-lg font-bold text-amber-600">{stats.due_cards}</div>
          <div className="text-[10px] text-gray-400">待复习</div>
        </div>
        <div className="text-center p-2 bg-emerald-50 rounded-lg">
          <div className="text-lg font-bold text-emerald-600">{stats.scheduled_cards}</div>
          <div className="text-[10px] text-gray-400">已安排</div>
        </div>
      </div>
    </div>
  );
}
