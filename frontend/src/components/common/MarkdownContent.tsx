'use client';

import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface MarkdownContentProps {
  children: string | null | undefined;
  className?: string;
}

export function MarkdownContent({ children, className }: MarkdownContentProps) {
  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          p: ({ children: pChildren, ...props }) => (
            <p className="my-1 first:mt-0 last:mb-0" {...props}>{pChildren}</p>
          ),
        }}
      >
        {children || ''}
      </ReactMarkdown>
    </div>
  );
}
