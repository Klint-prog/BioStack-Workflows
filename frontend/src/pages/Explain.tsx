import type { ExplainResponse, Project, Run } from '../api/client';
import ExplainPanel from '../components/ExplainPanel';
import RunTable from '../components/RunTable';

type ExplainProps = {
  runs: Run[];
  projects: Project[];
  selectedProject: string;
  result?: ExplainResponse | null;
  loading: boolean;
  onSelectProject: (projectName: string) => void;
  onExplain: (run: Run) => void;
};

export default function Explain({ runs, projects, selectedProject, result, loading, onSelectProject, onExplain }: ExplainProps) {
  return (
    <div className="stack">
      <section className="card">
        <div className="section-heading">
          <div>
            <h2>Explain operacional mock</h2>
            <p className="warning">AVISO: Não usar para diagnóstico ou interpretação clínica.</p>
            <p className="muted">O provider mock é usado por padrão para explicar logs e metadados de execução sem chamada externa.</p>
          </div>
          <label className="compact-field">
            Projeto
            <select value={selectedProject} onChange={(event) => onSelectProject(event.target.value)}>
              <option value="">Todos</option>
              {projects.map((project) => <option key={project.database_id ?? project.name} value={project.name}>{project.name}</option>)}
            </select>
          </label>
        </div>
        <RunTable runs={runs} onExplain={onExplain} />
      </section>
      <ExplainPanel result={result} loading={loading} />
    </div>
  );
}
