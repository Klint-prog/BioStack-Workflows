import type { Project } from '../api/client';
import ProjectForm from '../components/ProjectForm';

type ProjectsProps = {
  projects: Project[];
  selectedProject: string;
  onSelectProject: (projectName: string) => void;
  onCreateProject: (payload: { name: string; template: string; force: boolean }) => Promise<void>;
  onRunDryRun: (projectName: string) => Promise<void>;
  onOpenRuns: (projectName: string) => void;
  onOpenReports: (projectName: string) => void;
};

export default function Projects({ projects, selectedProject, onSelectProject, onCreateProject, onRunDryRun, onOpenRuns, onOpenReports }: ProjectsProps) {
  return (
    <div className="stack">
      <ProjectForm onSubmit={onCreateProject} />
      <section className="card">
        <div className="section-heading">
          <div>
            <h2>Projetos</h2>
            <p className="muted">Projetos reais retornados pela API, com ações de execução, runs e relatórios.</p>
          </div>
          <strong>{projects.length} projeto(s)</strong>
        </div>
        {projects.length === 0 ? <p className="muted">Nenhum projeto encontrado. Crie o primeiro projeto acima.</p> : (
          <div className="project-list">
            {projects.map((project) => {
              const isSelected = selectedProject === project.name;
              return (
                <article key={project.database_id ?? project.name} className={`project-item ${isSelected ? 'selected' : ''}`}>
                  <div>
                    <strong>{project.name}</strong>
                    <p className="muted">Template {project.template} · Workflow {project.workflow}</p>
                    <small className="path-text">{project.path}</small>
                  </div>
                  <div className="project-meta">
                    <span>{project.reports_count} relatório(s)</span>
                    {project.database_id ? <small>ID banco: {project.database_id}</small> : <small>Descoberto no workspace</small>}
                  </div>
                  <div className="button-row">
                    <button type="button" className="secondary" onClick={() => onSelectProject(isSelected ? '' : project.name)}>{isSelected ? 'Limpar seleção' : 'Selecionar'}</button>
                    <button type="button" onClick={() => onRunDryRun(project.name)}>Executar dry-run</button>
                    <button type="button" className="secondary" onClick={() => onOpenRuns(project.name)}>Ver runs</button>
                    <button type="button" className="secondary" onClick={() => onOpenReports(project.name)}>Ver relatórios</button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
