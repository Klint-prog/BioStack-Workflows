import type { Run } from '../api/client';
import StatusBadge from './StatusBadge';

type RunTableProps = { runs: Run[]; onExplain?: (run: Run) => void };

function formatDate(value?: string | null) {
  if (!value) return 'não informado';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function RunTable({ runs, onExplain }: RunTableProps) {
  if (runs.length === 0) return <p className="muted">Nenhuma execução registrada ainda para o filtro atual.</p>;

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Run</th>
            <th>Projeto</th>
            <th>Status</th>
            <th>Workflow</th>
            <th>Dry-run</th>
            <th>Retorno</th>
            <th>Datas</th>
            <th>Artefatos</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.database_id ?? `${run.project_name}-${run.run_id}`}>
              <td><code>{run.run_id}</code></td>
              <td>{run.project_name}</td>
              <td><StatusBadge status={run.status} /></td>
              <td>{run.workflow}<br /><small className="muted">profile: {run.profile}</small></td>
              <td>{run.dry_run ? 'sim' : 'não'}</td>
              <td>{run.return_code ?? 'pendente'}</td>
              <td>
                <small>Criado: {formatDate(run.created_at)}</small><br />
                <small>Atualizado: {formatDate(run.updated_at)}</small>
              </td>
              <td>
                <small>Log: {run.log_path || 'pendente'}</small><br />
                <small>JSON: {run.report_json_path || 'pendente'}</small><br />
                <small>HTML: {run.report_html_path || 'pendente'}</small>
              </td>
              <td><button type="button" onClick={() => onExplain?.(run)} disabled={!onExplain}>Explain mock</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
