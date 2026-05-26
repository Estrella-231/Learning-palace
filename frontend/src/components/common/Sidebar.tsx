'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageCircle, GitBranch, BookOpen, GraduationCap, Plus, X, Loader2 } from 'lucide-react';
import { useCourseStore } from '@/stores/courseStore';

const NAV_ITEMS = [
  { href: '/chat', label: '学习对话', icon: MessageCircle },
  { href: '/map', label: '知识地图', icon: GitBranch },
  { href: '/review', label: '复习中心', icon: GraduationCap },
];

export function Sidebar() {
  const pathname = usePathname();
  const courses = useCourseStore((s) => s.courses);
  const loading = useCourseStore((s) => s.loading);
  const selectedCourseId = useCourseStore((s) => s.selectedCourseId);
  const selectCourse = useCourseStore((s) => s.selectCourse);
  const createCourse = useCourseStore((s) => s.createCourse);
  const deleteCourse = useCourseStore((s) => s.deleteCourse);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setDeletingId(id);
    try {
      await deleteCourse(id);
    } catch {
      // ignore
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-4 border-b border-gray-100">
        <Link href="/chat" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-primary-600 flex items-center justify-center">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-base text-gray-800">知识宫殿</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="p-3 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Courses */}
      <div className="flex-1 overflow-y-auto p-3 border-t border-gray-100">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">课程</span>
          <button
            onClick={() => createCourse(`新课程 ${new Date().toLocaleDateString('zh-CN')}`)}
            className="p-1 rounded-md hover:bg-gray-100 transition-colors"
            title="创建课程"
          >
            <Plus className="w-3.5 h-3.5 text-gray-400" />
          </button>
        </div>
        {loading ? (
          <div className="flex items-center gap-1.5 text-xs text-gray-400 py-2">
            <Loader2 className="w-3 h-3 animate-spin" />
            加载中...
          </div>
        ) : courses.length === 0 ? (
          <p className="text-xs text-gray-400 py-2">暂无课程，点击 + 创建</p>
        ) : (
          courses.map((course) => (
            <div key={course.id} className="group relative">
              <button
                onClick={() => selectCourse(course.id)}
                className={`w-full text-left px-2.5 py-1.5 rounded-md text-sm truncate transition-colors ${
                  course.id === selectedCourseId
                    ? 'bg-primary-50 text-primary-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {course.name}
              </button>
              <button
                onClick={(e) => handleDelete(e, course.id)}
                disabled={deletingId === course.id}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 p-0.5 rounded opacity-0 group-hover:opacity-100 hover:bg-red-50 text-gray-400 hover:text-red-500 transition-all disabled:opacity-50"
                title="删除课程"
              >
                {deletingId === course.id ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <X className="w-3 h-3" />
                )}
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
