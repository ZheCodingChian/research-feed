import { useEffect, useRef } from 'react';
import renderMathInElement from 'katex/contrib/auto-render';
import 'katex/dist/katex.min.css';

interface LaTeXTextProps {
  children: string;
  className?: string;
}

export function LaTeXText({ children, className = '' }: LaTeXTextProps) {
  const containerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      const processedText = preprocessLatex(children);
      containerRef.current.innerHTML = processedText;

      renderMathInElement(containerRef.current, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\\[', right: '\\]', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
        ],
        throwOnError: false,
        trust: false,
      });
    } catch (error) {
      containerRef.current.textContent = children;
    }
  }, [children]);

  return <span ref={containerRef} className={`break-words ${className}`} />;
}

function preprocessLatex(text: string): string {
  return text
    .replace(/\\textit\{([^}]+)\}/g, '<em>$1</em>')
    .replace(/\\textbf\{([^}]+)\}/g, '<strong>$1</strong>')
    .replace(/\\texttt\{([^}]+)\}/g, '<code>$1</code>')
    .replace(/\\emph\{([^}]+)\}/g, '<em>$1</em>')
    .replace(/\\textcolor\{red\}\{([^}]+)\}/g, '<span style="color: #dc2626;">$1</span>')
    .replace(/\\textcolor\{blue\}\{([^}]+)\}/g, '<span style="color: #2563eb;">$1</span>')
    .replace(/\\textcolor\{green\}\{([^}]+)\}/g, '<span style="color: #16a34a;">$1</span>');
}
