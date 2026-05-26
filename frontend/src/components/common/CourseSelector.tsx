'use client';

import { useCourseStore } from '@/stores/courseStore';
import { Loader2 } from 'lucide-react';

export function CourseSelector() {
  const courses = useCourseStore((s) => s.courses);
  const loading = useCourseStore((s) => s.loading);
  const selectedCourseId = useCourseStore((s) => s.selectedCourseId);
  const selectCourse = useCourseStore((s) => s.selectCourse);

  if (loading) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-gray-400 px-2 py-1.5">
        <Loader2 className="w-3 h-3 animate-spin" />
        加载中
      </div>
    );
  }

  if (courses.length === 0) return null;

  return (
    <select
      value={selectedCourseId || ''}
      onChange={(e) => selectCourse(e.target.value)}
      className="text-sm border border-gray-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:ring-1 focus:ring-primary-200"
    >
      {courses.map((c) => (
        <option key={c.id} value={c.id}>
          {c.name}
        </option>
      ))}
    </select>
  );
}
