import type { Project, ReportSummary, Run } from '../api/client';
import StatusBadge from '../components/StatusBadge';

type DashboardProps = { projects: Project[]; runs: Run[]; reports: ReportSummary[] };

export default function Dashboard({ projects, runs, reports }: DashboardProps) {
  const lastRun = runs[0];
  return (
    <div className="grid">
      <section className="card metric"><span>Projetos</span><strong>{projects.length}</strong></section>
      <section className="card metric"><span>Runs</span><strong>{runs.length}</strong></section>
      <section className="card metric"><span>Relatórios</span><strong>{reports.length}</strong></section>
      <section className="card metric"><span>Último status</span>{lastRun ? <StatusBadge status={lastRun.status} /> : <strong>sem runs</strong>}</section>
    </div>
  );
}
