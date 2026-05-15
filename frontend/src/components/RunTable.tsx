import type { Run } from '../api/client';
import StatusBadge from './StatusBadge';

type RunTableProps = { runs: Run[]; onExplain?: (run: Run) => void };

export default function RunTable({ runs, onExplain }: RunTableProps) {
  if (runs.length === 0) return <p className="muted">Nenhuma execução registrada ainda.</p>;

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr><th>Run</th><th>Projeto</th><th>Status</th><th>Workflow</th><th>Dry-run</th><th>Relatório</th><th>Ação</th></tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.database_id ?? `${run.project_name}-${run.run_id}`}>
              <td>{run.run_id}</td><td>{run.project_name}</td><td><StatusBadge status={run.status} /></td><td>{run.workflow}</td><td>{run.dry_run ? 'sim' : 'não'}</td><td>{run.report_html_path || run.report_json_path || 'pendente'}</td>
              <td><button type="button" onClick={() => onExplain?.(run)}>Explain mock</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
