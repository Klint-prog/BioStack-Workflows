import { useEffect, useMemo, useState } from 'react';
import { api, type ExplainResponse, type Project, type ReportDetail, type ReportSummary, type Run } from './api/client';
import Dashboard from './pages/Dashboard';
import Explain from './pages/Explain';
import Projects from './pages/Projects';
import Reports from './pages/Reports';
import Runs from './pages/Runs';

type Page = 'dashboard' | 'projects' | 'runs' | 'reports' | 'explain';

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [projects, setProjects] = useState<Project[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null);
  const [explainResult, setExplainResult] = useState<ExplainResponse | null>(null);
  const [explainLoading, setExplainLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const pages: { id: Page; label: string }[] = useMemo(() => [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'projects', label: 'Projects' },
    { id: 'runs', label: 'Runs' },
    { id: 'reports', label: 'Reports' },
    { id: 'explain', label: 'Explain' }
  ], []);

  async function refresh() {
    setError('');
    try {
      const [projectList, runList, reportList] = await Promise.all([
        api.listProjects(), api.listRuns(), api.listReports()
      ]);
      setProjects(projectList);
      setRuns(runList);
      setReports(reportList);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao carregar dados da API.');
    }
  }

  useEffect(() => { void refresh(); }, []);

  async function handleCreateProject(payload: { name: string; template: string; force: boolean }) {
    setMessage('');
    setError('');
    try {
      const response = await api.createProject(payload);
      setMessage(`Projeto criado: ${response.project.name}`);
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
      setMessage(`Dry-run enfileirado: ${run.run_id}`);
      await refresh();
      setPage('runs');
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao enfileirar dry-run.');
    }
  }

  async function handleOpenReport(report: ReportSummary) {
    setError('');
    try {
      const detail = await api.getReport(report.project_name, report.run_id);
      setSelectedReport(detail);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Falha ao carregar relatório.');
    }
  }

  async function handleExplain(run: Run) {
    setExplainLoading(true);
    setExplainResult(null);
    setError('');
    try {
      const result = await api.explain({ project_name: run.project_name, run: run.run_id, provider: 'mock' });
      setExplainResult(result);
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
          <p className="eyebrow">BioStack Workflows · v0.2.0 phase_13</p>
          <h1>Frontend React/Vite para a Docker Platform Edition</h1>
          <p>Crie projetos, enfileire dry-runs, acompanhe status, visualize relatórios e rode explain mock.</p>
        </div>
        <button type="button" onClick={() => void refresh()}>Atualizar</button>
      </header>

      <nav className="tabs">
        {pages.map((item) => (
          <button key={item.id} type="button" className={page === item.id ? 'active' : ''} onClick={() => setPage(item.id)}>
            {item.label}
          </button>
        ))}
      </nav>

      {message ? <p className="notice">{message}</p> : null}
      {error ? <p className="error">{error}</p> : null}

      {page === 'dashboard' ? <Dashboard projects={projects} runs={runs} reports={reports} /> : null}
      {page === 'projects' ? <Projects projects={projects} onCreateProject={handleCreateProject} onRunDryRun={handleDryRun} /> : null}
      {page === 'runs' ? <Runs runs={runs} onExplain={handleExplain} /> : null}
      {page === 'reports' ? <Reports reports={reports} selectedReport={selectedReport} onOpenReport={handleOpenReport} /> : null}
      {page === 'explain' ? <Explain runs={runs} result={explainResult} loading={explainLoading} onExplain={handleExplain} /> : null}
    </main>
  );
}
