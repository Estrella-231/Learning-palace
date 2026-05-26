'use client';

import { useEffect } from 'react';
import './globals.css';
import { Sidebar } from '@/components/common/Sidebar';
import { useCourseStore } from '@/stores/courseStore';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const fetchCourses = useCourseStore((s) => s.fetchCourses);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  return (
    <html lang="zh-CN">
      <body className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
