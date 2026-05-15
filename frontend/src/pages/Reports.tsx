import type { Project, ReportDetail, ReportSummary } from '../api/client';
import LogViewer from '../components/LogViewer';
import ReportLink from '../components/ReportLink';

type ReportsProps = {
  reports: ReportSummary[];
  projects: Project[];
  selectedProject: string;
  selectedReport?: ReportDetail | null;
  loading: boolean;
  onSelectProject: (projectName: string) => void;
  onOpenReport: (report: ReportSummary) => void;
  onRefresh: () => Promise<void>;
};

export default function Reports({ reports, projects, selectedProject, selectedReport, loading, onSelectProject, onOpenReport, onRefresh }: ReportsProps) {
  return (
    <div className="stack">
      <section className="card">
        <div className="section-heading">
          <div>
            <h2>Relatórios</h2>
            <p className="muted">Relatórios reais vindos de GET /api/v1/reports. O JSON é aberto por GET /api/v1/reports/{'{project_name}'}/{'{run_id}'}.</p>
          </div>
          <div className="toolbar">
            <label className="compact-field">
              Filtrar projeto
              <select value={selectedProject} onChange={(event) => onSelectProject(event.target.value)}>
                <option value="">Todos</option>
                {projects.map((project) => <option key={project.database_id ?? project.name} value={project.name}>{project.name}</option>)}
              </select>
            </label>
            <button type="button" onClick={() => void onRefresh()} disabled={loading}>{loading ? 'Atualizando...' : 'Atualizar'}</button>
          </div>
        </div>
        {reports.length === 0 ? <p className="muted">Nenhum relatório encontrado para o filtro atual.</p> : (
          <div className="report-list">
            {reports.map((report) => <ReportLink key={`${report.project_name}-${report.run_id}`} report={report} onOpen={onOpenReport} />)}
          </div>
        )}
      </section>
      {selectedReport ? <LogViewer title={`Relatório JSON — ${selectedReport.project_name}/${selectedReport.run_id}`} content={selectedReport.metadata} /> : null}
    </div>
  );
}
