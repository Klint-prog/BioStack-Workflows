type LogViewerProps = {
  title: string;
  content: unknown;
};

export default function LogViewer({ title, content }: LogViewerProps) {
  return (
    <section className="card">
      <h3>{title}</h3>
      <pre>{typeof content === 'string' ? content : JSON.stringify(content, null, 2)}</pre>
    </section>
  );
}
