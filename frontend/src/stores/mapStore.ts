import { create } from 'zustand';
import type { MapData, KnowledgeNode, KnowledgeEdge } from '@/types';
import * as api from '@/lib/api';

interface MapState {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
  loading: boolean;
  selectedNodeId: string | null;

  fetchMap: (courseId: string) => Promise<void>;
  selectNode: (id: string | null) => void;
  addNodes: (nodes: KnowledgeNode[], edges: KnowledgeEdge[]) => void;
}

export const useMapStore = create<MapState>((set) => ({
  nodes: [],
  edges: [],
  loading: false,
  selectedNodeId: null,

  fetchMap: async (courseId: string) => {
    set({ loading: true });
    try {
      const data = await api.getMapData(courseId);
      set({ nodes: data.nodes, edges: data.edges, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  selectNode: (id: string | null) => set({ selectedNodeId: id }),

  addNodes: (newNodes: KnowledgeNode[], newEdges: KnowledgeEdge[]) => {
    set((s) => ({
      nodes: [...s.nodes, ...newNodes],
      edges: [...s.edges, ...newEdges],
    }));
  },
}));
