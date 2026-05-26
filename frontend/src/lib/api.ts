import type {
  ChatRequest,
  ChatResponse,
  Course,
  MapData,
  NodeDetail,
  ReviewCard,
  ReviewStats,
  Session,
} from '@/types';

const BASE_URL = '/api';
const USER_ID_KEY = 'lp-user-id';

function getUserId(): string {
  if (typeof window === 'undefined') return '';
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      'x-user-id': getUserId(),
    },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

// Chat
export async function sendMessage(req: ChatRequest): Promise<ChatResponse> {
  return fetchJson<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

// Courses
export async function getCourses(): Promise<Course[]> {
  return fetchJson<Course[]>('/courses');
}

export async function createCourse(name: string, description?: string): Promise<Course> {
  return fetchJson<Course>('/courses', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  });
}

export async function deleteCourse(courseId: string): Promise<void> {
  await fetchJson(`/courses/${courseId}`, { method: 'DELETE' });
}

// Sessions
export async function getSessions(courseId: string): Promise<Session[]> {
  return fetchJson<Session[]>(`/courses/${courseId}/sessions`);
}

export async function createSession(courseId: string): Promise<Session> {
  return fetchJson<Session>(`/courses/${courseId}/sessions`, { method: 'POST' });
}

// Map
export async function getMapData(courseId: string): Promise<MapData> {
  return fetchJson<MapData>(`/map/${courseId}`);
}

// Nodes
export async function getNodeDetail(nodeId: string): Promise<NodeDetail> {
  return fetchJson<NodeDetail>(`/nodes/${nodeId}`);
}

export async function updateNode(
  nodeId: string,
  data: Partial<{ position_x: number; position_y: number; title: string; summary: string }>
): Promise<void> {
  await fetchJson(`/nodes/${nodeId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteNode(nodeId: string): Promise<void> {
  await fetchJson(`/nodes/${nodeId}`, { method: 'DELETE' });
}

// Review
export async function getDueCards(courseId?: string): Promise<ReviewCard[]> {
  const params = courseId ? `?course_id=${courseId}` : '';
  return fetchJson<ReviewCard[]>(`/review/due${params}`);
}

export async function submitReview(cardId: string, rating: 'again' | 'hard' | 'good' | 'easy') {
  return fetchJson<{
    status: string;
    next_review_at: string;
    stability: number;
    retrievability: number;
    review_count: number;
  }>(`/review/${cardId}?rating=${rating}`, { method: 'POST' });
}

export async function getReviewStats(courseId?: string): Promise<ReviewStats> {
  const params = courseId ? `?course_id=${courseId}` : '';
  return fetchJson<ReviewStats>(`/review/stats${params}`);
}
