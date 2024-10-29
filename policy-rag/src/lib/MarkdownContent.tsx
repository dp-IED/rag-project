import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownContentProps {
  content: string;
  className?: string;
}

const MarkdownContent: React.FC<MarkdownContentProps> = ({
  content,
  className = "",
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="p-6">
        <div className="text-sm text-slate-600 mb-4">Analysis</div>
        <div className={`prose prose-slate max-w-3xl mx-auto ${className}`}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Customize heading styles
              h1: ({ node, ...props }) => (
                <h1
                  className="text-3xl font-bold text-slate-900 mb-6"
                  {...props}
                />
              ),
              h2: ({ node, ...props }) => (
                <h2
                  className="text-2xl font-semibold text-slate-800 mb-4 mt-8"
                  {...props}
                />
              ),

              // Customize paragraph styles
              p: ({ node, ...props }) => (
                <p
                  className="text-base text-slate-700 leading-relaxed mb-4"
                  {...props}
                />
              ),

              // Customize list styles
              ul: ({ node, ...props }) => (
                <ul className="space-y-2 mb-6" {...props} />
              ),
              li: ({ node, ...props }) => (
                <li className="flex space-x-3">
                  <span className="text-slate-400 mt-1">•</span>
                  <span className="text-slate-700 flex-1" {...props} />
                </li>
              ),

              // Customize bold text
              strong: ({ node, ...props }) => (
                <strong className="font-semibold text-slate-900" {...props} />
              ),

              // Customize blockquotes
              blockquote: ({ node, ...props }) => (
                <blockquote
                  className="border-l-4 border-slate-200 pl-4 italic text-slate-600"
                  {...props}
                />
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default MarkdownContent;
