import type { ExplainResponse, Run } from '../api/client';
import ExplainPanel from '../components/ExplainPanel';
import RunTable from '../components/RunTable';

type ExplainProps = {
  runs: Run[];
  result?: ExplainResponse | null;
  loading: boolean;
  onExplain: (run: Run) => void;
};

export default function Explain({ runs, result, loading, onExplain }: ExplainProps) {
  return (
    <div className="stack">
      <section className="card">
        <h2>Explain operacional mock</h2>
        <p className="muted">Use apenas para troubleshooting técnico; não há interpretação clínica.</p>
        <RunTable runs={runs} onExplain={onExplain} />
      </section>
      <ExplainPanel result={result} loading={loading} />
    </div>
  );
}
