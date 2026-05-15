import type { HealthResponse, Project, ReportSummary, Run } from '../api/client';
import StatusBadge from '../components/StatusBadge';

type DashboardProps = {
  projects: Project[];
  runs: Run[];
  reports: ReportSummary[];
  health: HealthResponse | null;
  loading: { health: boolean; projects: boolean; runs: boolean; reports: boolean };
  lastUpdated: string | null;
  selectedProject: string;
  onSelectProject: (projectName: string) => void;
};

function countByStatus(runs: Run[]) {
  return runs.reduce<Record<string, number>>((accumulator, run) => {
    const key = run.status.toUpperCase();
    accumulator[key] = (accumulator[key] ?? 0) + 1;
    return accumulator;
  }, {});
}

export default function Dashboard({ projects, runs, reports, health, loading, lastUpdated, selectedProject, onSelectProject }: DashboardProps) {
  const lastRun = runs[0];
  const statusCount = countByStatus(runs);
  const activeRuns = runs.filter((run) => ['QUEUED', 'RUNNING'].includes(run.status.toUpperCase()));

  return (
    <div className="stack">
      <section className="grid">
        <article className="card metric">
          <span>Status da API</span>
          <strong>{loading.health ? '...' : health?.status ?? 'offline'}</strong>
          <small>{health ? 'Healthcheck real em /api/v1/health' : 'Sem resposta do healthcheck'}</small>
        </article>
        <article className="card metric">
          <span>Projetos</span>
          <strong>{loading.projects ? '...' : projects.length}</strong>
          <small>Dados vindos de GET /api/v1/projects</small>
        </article>
        <article className="card metric">
          <span>Execuções</span>
          <strong>{loading.runs ? '...' : runs.length}</strong>
          <small>{activeRuns.length > 0 ? `${activeRuns.length} run(s) em fila/processamento` : 'Nenhuma run ativa'}</small>
        </article>
        <article className="card metric">
          <span>Relatórios</span>
          <strong>{loading.reports ? '...' : reports.length}</strong>
          <small>JSONs listados por GET /api/v1/reports</small>
        </article>
      </section>

      <section className="card dashboard-wide">
        <div className="section-heading">
          <div>
            <h2>Visão operacional</h2>
            <p className="muted">Última atualização: {lastUpdated ?? 'ainda não carregada'}</p>
          </div>
          <label className="compact-field">
            Projeto ativo
            <select value={selectedProject} onChange={(event) => onSelectProject(event.target.value)}>
              <option value="">Todos os projetos</option>
              {projects.map((project) => <option key={project.database_id ?? project.name} value={project.name}>{project.name}</option>)}
            </select>
          </label>
        </div>

        <div className="status-grid">
          {['QUEUED', 'RUNNING', 'SUCCEEDED', 'FAILED'].map((status) => (
            <div key={status} className="status-tile">
              <StatusBadge status={status} />
              <strong>{statusCount[status] ?? 0}</strong>
            </div>
          ))}
        </div>

        <div className="last-run">
          <h3>Última execução registrada</h3>
          {lastRun ? (
            <dl>
              <div><dt>Run</dt><dd>{lastRun.run_id}</dd></div>
              <div><dt>Projeto</dt><dd>{lastRun.project_name}</dd></div>
              <div><dt>Status</dt><dd><StatusBadge status={lastRun.status} /></dd></div>
              <div><dt>Workflow</dt><dd>{lastRun.workflow}</dd></div>
              <div><dt>Atualizado em</dt><dd>{lastRun.updated_at ?? 'não informado'}</dd></div>
            </dl>
          ) : <p className="muted">Nenhuma execução registrada até o momento.</p>}
        </div>
      </section>
    </div>
  );
}
