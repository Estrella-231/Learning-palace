import { create } from 'zustand';
import type { Course } from '@/types';
import * as api from '@/lib/api';

interface CourseState {
  courses: Course[];
  selectedCourseId: string | null;
  loading: boolean;

  fetchCourses: () => Promise<void>;
  selectCourse: (id: string) => void;
  createCourse: (name: string, description?: string) => Promise<Course>;
  deleteCourse: (id: string) => Promise<void>;
}

export const useCourseStore = create<CourseState>((set, get) => ({
  courses: [],
  selectedCourseId: null,
  loading: false,

  fetchCourses: async () => {
    set({ loading: true });
    try {
      const courses = await api.getCourses();
      set({ courses, loading: false });
      if (courses.length > 0 && !get().selectedCourseId) {
        set({ selectedCourseId: courses[0].id });
      }
    } catch {
      set({ loading: false });
    }
  },

  selectCourse: (id: string) => set({ selectedCourseId: id }),

  createCourse: async (name: string, description?: string) => {
    const course = await api.createCourse(name, description);
    set((s) => ({ courses: [...s.courses, course], selectedCourseId: course.id }));
    return course;
  },

  deleteCourse: async (id: string) => {
    await api.deleteCourse(id);
    set((s) => ({
      courses: s.courses.filter((c) => c.id !== id),
      selectedCourseId: s.selectedCourseId === id ? null : s.selectedCourseId,
    }));
  },
}));
