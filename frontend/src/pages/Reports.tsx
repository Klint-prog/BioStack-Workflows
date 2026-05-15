import type { ReportDetail, ReportSummary } from '../api/client';
import LogViewer from '../components/LogViewer';
import ReportLink from '../components/ReportLink';

type ReportsProps = {
  reports: ReportSummary[];
  selectedReport?: ReportDetail | null;
  onOpenReport: (report: ReportSummary) => void;
};

export default function Reports({ reports, selectedReport, onOpenReport }: ReportsProps) {
  return (
    <div className="stack">
      <section className="card">
        <h2>Relatórios</h2>
        {reports.length === 0 ? <p className="muted">Nenhum relatório gerado ainda.</p> : (
          <div className="report-list">
            {reports.map((report) => <ReportLink key={`${report.project_name}-${report.run_id}`} report={report} onOpen={onOpenReport} />)}
          </div>
        )}
      </section>
      {selectedReport ? <LogViewer title="Metadados do relatório" content={selectedReport.metadata} /> : null}
    </div>
  );
}
