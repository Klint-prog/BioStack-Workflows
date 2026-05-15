import { useCallback, useEffect, useMemo, useState } from 'react';
import { api, type ExplainResponse, type HealthResponse, type Project, type ReportDetail, type ReportSummary, type Run } from './api/client';
import Dashboard from './pages/Dashboard';
import Explain from './pages/Explain';
import Projects from './pages/Projects';
import Reports from './pages/Reports';
import Runs from './pages/Runs';

type Page = 'dashboard' | 'projects' | 'runs' | 'reports' | 'explain';

type LoadState = {
  health: boolean;
  projects: boolean;
  runs: boolean;
  reports: boolean;
};

const initialLoadState: LoadState = { health: false, projects: false, runs: false, reports: false };

function isActiveRun(run: Run) {
  return ['QUEUED', 'RUNNING'].includes(run.status.toUpperCase());
}

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [projects, setProjects] = useState<Project[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [selectedProject, setSelectedProject] = useState<string>('');
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null);
  const [explainResult, setExplainResult] = useState<ExplainResponse | null>(null);
  const [explainLoading, setExplainLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState<LoadState>(initialLoadState);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const pages: { id: Page; label: string; description: string }[] = useMemo(() => [
    { id: 'dashboard', label: 'Dashboard', description: 'Métricas reais da API' },
    { id: 'projects', label: 'Projetos', description: 'Criar e operar projetos' },
    { id: 'runs', label: 'Execuções', description: 'Fila, worker e status' },
    { id: 'reports', label: 'Relatórios', description: 'JSON e metadados' },
    { id: 'explain', label: 'Explain', description: 'Troubleshooting mock' }
  ], []);

  const filteredRuns = useMemo(
    () => selectedProject ? runs.filter((run) => run.project_name === selectedProject) : runs,
    [runs, selectedProject]
  );

  const filteredReports = useMemo(
    () => selectedProject ? reports.filter((report) => report.project_name === selectedProject) : reports,
    [reports, selectedProject]
  );

  const refresh = useCallback(async () => {
    setError('');
    setLoading({ health: true, projects: true, runs: true, reports: true });
    try {
      const [healthResult, projectList, runList, reportList] = await Promise.all([
        api.health(), api.listProjects(), api.listRuns(), api.listReports()
      ]);
      setHealth(healthResult);
      setProjects(projectList);
      setRuns(runList);
      setReports(reportList);
      setLastUpdated(new Date().toLocaleString());
    } catch (caught) {
      setHealth(null);
      setError(caught instanceof Error ? caught.message : 'Falha ao carregar dados reais da API.');
    } finally {
      setLoading(initialLoadState);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  useEffect(() => {
    if (!runs.some(isActiveRun)) return undefined;
    const interval = window.setInterval(() => { void refresh(); }, 8000);
    return () => window.clearInterval(interval);
  }, [refresh, runs]);

  async function handleCreateProject(payload: { name: string; template: string; force: boolean }) {
    setMessage('');
    setError('');
    try {
      const response = await api.createProject(payload);
      setSelectedProject(response.project.name);
      setMessage(`Projeto criado com sucesso: ${response.project.name}`);
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao criar projeto.');
    }
  }

  async function handleDryRun(projectName: string) {
    setMessage('');
    setError('');
    try {
      const run = await api.createRun({ project_name: projectName, dry_run: true });
      setSelectedProject(projectName);
      setMessage(`Dry-run enfileirado no worker: ${run.run_id}`);
      await refresh();
      setPage('runs');
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao enfileirar dry-run.');
    }
  }

  async function handleOpenReport(report: ReportSummary) {
    setSelectedReport(null);
    setError('');
    try {
      const detail = await api.getReport(report.project_name, report.run_id);
      setSelectedReport(detail);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao carregar relatório JSON.');
    }
  }

  async function handleExplain(run: Run) {
    setExplainLoading(true);
    setExplainResult(null);
    setError('');
    try {
      const result = await api.explain({ project_name: run.project_name, run: run.run_id, provider: 'mock' });
      setExplainResult(result);
      setSelectedProject(run.project_name);
      setPage('explain');
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao executar explain mock.');
    } finally {
      setExplainLoading(false);
    }
  }

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">BioStack Workflows · Docker Platform Edition v0.2.0</p>
          <h1>Painel operacional para workflows de bioinformática</h1>
          <p>Crie projetos, execute dry-runs, acompanhe runs, visualize relatórios e gere troubleshooting operacional com provider mock.</p>
          <p className="flow-hint">Browser → Nginx → Frontend → API FastAPI → PostgreSQL/Redis/Worker</p>
        </div>
        <div className="hero-actions">
          <span className={health ? 'api-pill online' : 'api-pill offline'}>{health ? 'API online' : 'API offline'}</span>
          <button type="button" onClick={() => void refresh()} disabled={Object.values(loading).some(Boolean)}>
            {Object.values(loading).some(Boolean) ? 'Atualizando...' : 'Atualizar dados'}
          </button>
        </div>
      </header>

      <nav className="tabs" aria-label="Navegação operacional">
        {pages.map((item) => (
          <button key={item.id} type="button" className={page === item.id ? 'active' : ''} onClick={() => setPage(item.id)}>
            <strong>{item.label}</strong>
            <small>{item.description}</small>
          </button>
        ))}
      </nav>

      {message ? <p className="notice">{message}</p> : null}
      {error ? <p className="error">{error} <button type="button" className="inline-button" onClick={() => void refresh()}>Tentar novamente</button></p> : null}

      {page === 'dashboard' ? (
        <Dashboard
          projects={projects}
          runs={runs}
          reports={reports}
          health={health}
          loading={loading}
          lastUpdated={lastUpdated}
          selectedProject={selectedProject}
          onSelectProject={setSelectedProject}
        />
      ) : null}
      {page === 'projects' ? (
        <Projects
          projects={projects}
          selectedProject={selectedProject}
          onSelectProject={setSelectedProject}
          onCreateProject={handleCreateProject}
          onRunDryRun={handleDryRun}
          onOpenRuns={(projectName) => { setSelectedProject(projectName); setPage('runs'); }}
          onOpenReports={(projectName) => { setSelectedProject(projectName); setPage('reports'); }}
        />
      ) : null}
      {page === 'runs' ? (
        <Runs
          runs={filteredRuns}
          projects={projects}
          selectedProject={selectedProject}
          onSelectProject={setSelectedProject}
          onExplain={handleExplain}
          onRefresh={refresh}
          loading={loading.runs}
        />
      ) : null}
      {page === 'reports' ? (
        <Reports
          reports={filteredReports}
          projects={projects}
          selectedProject={selectedProject}
          selectedReport={selectedReport}
          onSelectProject={setSelectedProject}
          onOpenReport={handleOpenReport}
          onRefresh={refresh}
          loading={loading.reports}
        />
      ) : null}
      {page === 'explain' ? (
        <Explain
          runs={filteredRuns}
          projects={projects}
          selectedProject={selectedProject}
          result={explainResult}
          loading={explainLoading}
          onSelectProject={setSelectedProject}
          onExplain={handleExplain}
        />
      ) : null}
    </main>
  );
}
