"use client";

import { useState } from "react";

interface ReportHtmlViewerProps {
  reportId: number;
}

export default function ReportHtmlViewer({ reportId }: ReportHtmlViewerProps) {
  const [height, setHeight] = useState(600);

  function handleLoad(e: React.SyntheticEvent<HTMLIFrameElement>) {
    try {
      const body = e.currentTarget.contentDocument?.body;
      if (body) {
        setHeight(Math.max(600, body.scrollHeight + 40));
      }
    } catch {
      // Cross-origin, keep default height
    }
  }

  return (
    <iframe
      src={`/api/reports/${reportId}/html`}
      className="w-full rounded-lg border border-[var(--border-color)]"
      style={{ height: `${height}px` }}
      onLoad={handleLoad}
      title="Report HTML"
    />
  );
}
