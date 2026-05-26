'use client';

import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { Lightbulb, ClipboardList, AlertTriangle, HelpCircle, LucideIcon } from 'lucide-react';

/** Strip LaTeX math delimiters for compact display */
function stripMath(text: string): string {
  return text
    .replace(/\$\$(.+?)\$\$/g, '$1')
    .replace(/\$(.+?)\$/g, '$1')
    .replace(/\\[a-zA-Z]+(\{[^}]*\})?/g, '');
}

const TYPE_ICONS: Record<string, LucideIcon> = {
  concept: Lightbulb,
  example: ClipboardList,
  misconception: AlertTriangle,
  question: HelpCircle,
};

interface ConceptNodeData {
  label: string;
  nodeType: string;
  summary: string;
  mastery: number;
  color: string;
}

export const ConceptNode = memo(({ data }: { data: ConceptNodeData }) => {
  const { label, nodeType, summary, mastery, color } = data;
  const Icon = TYPE_ICONS[nodeType] || Lightbulb;

  return (
    <div
      className="px-3.5 py-2.5 rounded-xl border-2 shadow-sm bg-white min-w-[160px] max-w-[240px] cursor-pointer hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200"
      style={{ borderColor: color }}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-300" />
      <div className="flex items-center gap-2 mb-1.5">
        <div
          className="w-5 h-5 rounded-md flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${color}18` }}
        >
          <Icon className="w-3 h-3" style={{ color }} />
        </div>
        <span className="font-semibold text-xs text-gray-800 truncate">{stripMath(label)}</span>
      </div>
      <p className="text-[11px] text-gray-500 line-clamp-2 leading-relaxed mb-2">
        {stripMath(summary)}
      </p>
      {/* Mastery bar */}
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.max(mastery * 100, 5)}%`,
              backgroundColor: color,
            }}
          />
        </div>
        <span className="text-[10px] font-medium text-gray-400 tabular-nums">
          {Math.round(mastery * 100)}%
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-gray-300" />
    </div>
  );
});

ConceptNode.displayName = 'ConceptNode';
