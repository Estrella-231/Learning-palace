'use client';

import { useEffect, useCallback, useState, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionLineType,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';

import { ConceptNode } from '@/components/map/ConceptNode';
import { useMapStore } from '@/stores/mapStore';
import { useCourseStore } from '@/stores/courseStore';
import { updateNode } from '@/lib/api';
import { Search } from 'lucide-react';

const nodeTypes = { conceptNode: ConceptNode };

const TYPE_COLORS: Record<string, string> = {
  concept: '#3b82f6',
  example: '#22c55e',
  misconception: '#ef4444',
  question: '#eab308',
};

const TYPE_LABELS: Record<string, string> = {
  concept: '概念',
  example: '例子',
  misconception: '误区',
  question: '问题',
};

/** Lay out nodes and edges using dagre for a readable graph */
function layoutGraph(
  nodes: any[],
  edges: any[],
): { nodes: any[]; edges: any[] } {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'TB', nodesep: 80, ranksep: 120 });

  for (const node of nodes) {
    g.setNode(node.id, { width: 220, height: 90 });
  }
  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  dagre.layout(g);

  const layoutedNodes = nodes.map((n) => {
    const pos = g.node(n.id);
    const hasSavedPosition = n.position.x !== 0 || n.position.y !== 0;
    return {
      ...n,
      position: hasSavedPosition
        ? n.position
        : { x: pos.x - 110, y: pos.y - 45 },
    };
  });

  return { nodes: layoutedNodes, edges };
}

export default function MapPage() {
  const router = useRouter();
  const selectedCourseId = useCourseStore((s) => s.selectedCourseId);
  const { nodes: rawNodes, edges: rawEdges, loading, fetchMap } = useMapStore();
  const [search, setSearch] = useState('');

  // Build and layout flow nodes/edges from raw data
  const layouted = useMemo(() => {
    const fNodes = rawNodes
      .filter((n) => !search || n.title.toLowerCase().includes(search.toLowerCase()))
      .map((n) => ({
        id: n.id,
        type: 'conceptNode',
        position: { x: n.position_x || 0, y: n.position_y || 0 },
        data: {
          label: n.title,
          nodeType: n.type,
          summary: n.summary,
          mastery: n.mastery,
          color: TYPE_COLORS[n.type] || TYPE_COLORS.concept,
        },
      }));

    const fEdges = rawEdges.map((e) => ({
      id: e.id,
      source: e.source_node_id,
      target: e.target_node_id,
      label: e.relation_type,
      type: ConnectionLineType.SmoothStep,
      animated: false,
      style: { stroke: '#94a3b8', strokeWidth: 1.5 },
      data: { relation_type: e.relation_type, confidence: e.confidence },
    }));

    return layoutGraph(fNodes, fEdges);
  }, [rawNodes, rawEdges, search]);

  const [nodes, setNodes, onNodesChange] = useNodesState(layouted.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layouted.edges);

  useEffect(() => {
    if (selectedCourseId) {
      fetchMap(selectedCourseId);
    }
  }, [selectedCourseId, fetchMap]);

  // Sync layout on data change, preserve user drags on updates
  const prevRawLen = useRef(rawNodes.length + rawEdges.length);
  useEffect(() => {
    const currentLen = rawNodes.length + rawEdges.length;
    if (currentLen !== prevRawLen.current) {
      setNodes(layouted.nodes);
      setEdges(layouted.edges);
      prevRawLen.current = currentLen;
    }
  }, [layouted, setNodes, setEdges, rawNodes.length, rawEdges.length]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: any) => {
      router.push(`/node/${node.id}`);
    },
    [router],
  );

  const onNodeDragStop = useCallback(
    (_: React.MouseEvent, node: any) => {
      updateNode(node.id, { position_x: node.position.x, position_y: node.position.y }).catch(
        console.error,
      );
    },
    [],
  );

  if (!selectedCourseId) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <p>请先在左侧选择一个课程</p>
      </div>
    );
  }

  return (
    <div className="h-full relative">
      {/* Top bar */}
      <div className="absolute top-0 left-0 right-0 z-10 px-4 py-2 bg-white/80 backdrop-blur border-b border-gray-100 flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索知识点..."
            className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-200"
          />
        </div>
        <div className="flex gap-3 text-xs">
          {Object.entries(TYPE_COLORS).map(([type, color]) => (
            <span key={type} className="flex items-center gap-1">
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: color }}
              />
              {TYPE_LABELS[type] || type}
            </span>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          加载中...
        </div>
      ) : (
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onNodeDragStop={onNodeDragStop}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          className="pt-12"
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
          <Controls />
          <MiniMap
            nodeColor={(n) => n.data?.color || '#3b82f6'}
            style={{ backgroundColor: '#f8fafc' }}
          />
        </ReactFlow>
      )}
    </div>
  );
}
