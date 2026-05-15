import type { ExplainResponse } from '../api/client';

type ExplainPanelProps = {
  result?: ExplainResponse | null;
  loading?: boolean;
};

export default function ExplainPanel({ result, loading = false }: ExplainPanelProps) {
  if (loading) return <section className="card"><p>Gerando explicação mock...</p></section>;
  if (!result) return <section className="card"><p className="muted">Selecione uma execução para explicar logs com o provider mock.</p></section>;

  return (
    <section className="card explain-panel">
      <h3>Explain mock — {result.run_id}</h3>
      <p className="warning">{result.clinical_warning}</p>
      <pre>{result.explanation}</pre>
    </section>
  );
}
