import { create } from 'zustand';
import type { KnowledgeNode, KnowledgeEdge, ReviewCard } from '@/types';
import { sendMessage as apiSendMessage } from '@/lib/api';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  courseId: string | null;
  isLoading: boolean;
  knowledgeNodes: KnowledgeNode[];
  knowledgeEdges: KnowledgeEdge[];
  reviewCards: ReviewCard[];

  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
  setCourse: (courseId: string) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessionId: null,
  courseId: null,
  isLoading: false,
  knowledgeNodes: [],
  knowledgeEdges: [],
  reviewCards: [],

  sendMessage: async (content: string) => {
    const state = get();
    // Guard against concurrent sends
    if (state.isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    set({ messages: [...state.messages, userMsg], isLoading: true });

    try {
      const data = await apiSendMessage({
        message: content,
        course_id: state.courseId ?? undefined,
        session_id: state.sessionId ?? undefined,
      });

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        timestamp: Date.now(),
      };

      set((s) => ({
        messages: [...s.messages, assistantMsg],
        isLoading: false,
        sessionId: data.session_id,
        courseId: data.course_id,
        // Accumulate knowledge across messages (dedupe by id)
        knowledgeNodes: [...s.knowledgeNodes, ...data.new_nodes.filter(
          (n) => !s.knowledgeNodes.some((existing) => existing.id === n.id)
        )],
        knowledgeEdges: [...s.knowledgeEdges, ...data.new_edges.filter(
          (e) => !s.knowledgeEdges.some((existing) => existing.id === e.id)
        )],
        reviewCards: [...s.reviewCards, ...data.review_cards.filter(
          (c) => !s.reviewCards.some((existing) => existing.id === c.id)
        )],
      }));
    } catch (err) {
      set({ isLoading: false });
      console.error('Chat error:', err);
    }
  },

  clearChat: () =>
    set({
      messages: [],
      sessionId: null,
      knowledgeNodes: [],
      knowledgeEdges: [],
      reviewCards: [],
    }),

  setCourse: (courseId: string) => set({ courseId }),
}));
