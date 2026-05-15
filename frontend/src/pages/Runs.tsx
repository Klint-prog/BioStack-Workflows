import type { Project, Run } from '../api/client';
import RunTable from '../components/RunTable';

type RunsProps = {
  runs: Run[];
  projects: Project[];
  selectedProject: string;
  loading: boolean;
  onSelectProject: (projectName: string) => void;
  onExplain: (run: Run) => void;
  onRefresh: () => Promise<void>;
};

export default function Runs({ runs, projects, selectedProject, loading, onSelectProject, onExplain, onRefresh }: RunsProps) {
  const activeRuns = runs.filter((run) => ['QUEUED', 'RUNNING'].includes(run.status.toUpperCase()));

  return (
    <section className="card">
      <div className="section-heading">
        <div>
          <h2>Runs e status do worker</h2>
          <p className="muted">Lista real de GET /api/v1/runs. Enquanto houver QUEUED/RUNNING, o painel atualiza automaticamente a cada 8 segundos.</p>
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
      {activeRuns.length > 0 ? <p className="notice">{activeRuns.length} execução(ões) ainda em fila/processamento.</p> : null}
      <RunTable runs={runs} onExplain={onExplain} />
    </section>
  );
}
