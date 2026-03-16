"use client";

interface SectionContentProps {
  html: string;
}

/**
 * Renders report section content. Content is rendered as plain text
 * for safety. The full HTML report is available via the iframe viewer.
 */
export default function SectionContent({ html }: SectionContentProps) {
  // Strip HTML tags and render as plain text paragraphs
  const text = html.replace(/<[^>]*>/g, "\n").trim();
  const paragraphs = text
    .split(/\n+/)
    .map((p) => p.trim())
    .filter(Boolean);

  return (
    <div className="space-y-2 text-sm text-[var(--text-secondary)]">
      {paragraphs.map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
    </div>
  );
}
