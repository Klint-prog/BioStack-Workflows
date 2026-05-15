import type { ReportSummary } from '../api/client';
import StatusBadge from './StatusBadge';

type ReportLinkProps = { report: ReportSummary; onOpen: (report: ReportSummary) => void };

export default function ReportLink({ report, onOpen }: ReportLinkProps) {
  return (
    <article className="card report-card">
      <div><strong>{report.run_id}</strong><p className="muted">{report.project_name} · {report.workflow}</p></div>
      <StatusBadge status={report.status} />
      <button type="button" onClick={() => onOpen(report)}>Ver JSON</button>
      <small>{report.html_path ?? report.json_path}</small>
    </article>
  );
}
