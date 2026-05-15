import type { ExplainResponse } from '../api/client';

type ExplainPanelProps = {
  result?: ExplainResponse | null;
  loading?: boolean;
};

export default function ExplainPanel({ result, loading = false }: ExplainPanelProps) {
  if (loading) return <section className="card"><p>Gerando troubleshooting operacional com provider mock...</p></section>;
  if (!result) return <section className="card"><p className="muted">Selecione uma execução com relatório disponível para gerar explain mock.</p></section>;

  return (
    <section className="card explain-panel">
      <div className="section-heading">
        <div>
          <h3>Explain mock — {result.run_id}</h3>
          <p className="muted">Projeto {result.project_name} · provider {result.provider} · status {result.status}</p>
        </div>
      </div>
      <p className="warning">{result.clinical_warning || 'AVISO: Não usar para diagnóstico ou interpretação clínica.'}</p>
      <div className="explain-grid">
        <article>
          <h4>Escopo</h4>
          <p>Troubleshooting técnico de logs e metadados operacionais.</p>
        </article>
        <article>
          <h4>Resposta</h4>
          <pre>{result.explanation}</pre>
        </article>
      </div>
    </section>
  );
}
