import type { Run } from '../api/client';
import RunTable from '../components/RunTable';

type RunsProps = { runs: Run[]; onExplain: (run: Run) => void };

export default function Runs({ runs, onExplain }: RunsProps) {
  return (
    <section className="card">
      <h2>Runs e status</h2>
      <RunTable runs={runs} onExplain={onExplain} />
    </section>
  );
}
