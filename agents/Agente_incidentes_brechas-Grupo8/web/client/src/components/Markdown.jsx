import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/* Los enlaces a otros .md del expediente cambian de pestaña; el resto abre en pestaña nueva. */
export default function Markdown({ text, onDoc }) {
  return (
    <div className="doc">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ children }) => <div className="tw"><table>{children}</table></div>,
          a: ({ href = '', children }) =>
            /\.md$/.test(href)
              ? <a href="#" onClick={e => { e.preventDefault(); onDoc && onDoc(href.replace(/^\.\//, '')); }}>{children}</a>
              : <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
        }}
      >{text}</ReactMarkdown>
    </div>
  );
}
