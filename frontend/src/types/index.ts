export interface KnowledgeNode {
  id: string;
  course_id?: string;
  title: string;
  type: 'concept' | 'example' | 'misconception' | 'question';
  summary: string;
  content?: string;
  mastery: number;
  position_x: number;
  position_y: number;
  source_message_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface KnowledgeEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: string;
  confidence: number;
  evidence?: string | null;
}

export interface ReviewCard {
  id: string;
  node_id: string;
  question: string;
  answer: string;
  card_type: 'basic' | 'contrast' | 'application';
  difficulty: number;
  next_review_at?: string;
  stability?: number;
  retrievability?: number;
  review_count?: number;
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  course_id: string;
  new_nodes: KnowledgeNode[];
  new_edges: KnowledgeEdge[];
  review_cards: ReviewCard[];
}

export interface ChatRequest {
  message: string;
  course_id?: string;
  session_id?: string;
}

export interface Course {
  id: string;
  name: string;
  description: string;
  created_at?: string;
}

export interface Session {
  id: string;
  course_id: string;
  title: string;
  created_at?: string;
}

export interface MapData {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
}

export interface NodeDetail {
  node: KnowledgeNode;
  source_message: {
    id: string;
    role: string;
    content: string;
    created_at: string;
  } | null;
  related_nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
  review_cards: ReviewCard[];
}

export interface ReviewStats {
  total_cards: number;
  due_cards: number;
  scheduled_cards: number;
}

// React Flow node/edge types
export interface FlowNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: {
    label: string;
    nodeType: KnowledgeNode['type'];
    summary: string;
    mastery: number;
  };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  data?: {
    relation_type: string;
    confidence: number;
  };
}
