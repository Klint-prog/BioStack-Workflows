import type { ReportSummary } from '../api/client';
import StatusBadge from './StatusBadge';

type ReportLinkProps = { report: ReportSummary; onOpen: (report: ReportSummary) => void };

function formatDate(value: string) {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function ReportLink({ report, onOpen }: ReportLinkProps) {
  return (
    <article className="card report-card">
      <div>
        <strong>{report.run_id}</strong>
        <p className="muted">{report.project_name} · {report.workflow} · {formatDate(report.started_at)}</p>
      </div>
      <StatusBadge status={report.status} />
      <div className="button-row">
        <button type="button" onClick={() => onOpen(report)}>Abrir JSON</button>
        {report.html_path ? <button type="button" className="secondary" title="A API atual informa o caminho HTML, mas não publica um endpoint dedicado de arquivo estático.">HTML disponível</button> : null}
      </div>
      <small>JSON: {report.json_path}</small>
      <small>{report.html_path ? `HTML: ${report.html_path}` : 'HTML: endpoint/arquivo público não informado pela API'}</small>
    </article>
  );
}
