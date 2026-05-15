import type { Project } from '../api/client';
import ProjectForm from '../components/ProjectForm';

type ProjectsProps = {
  projects: Project[];
  onCreateProject: (payload: { name: string; template: string; force: boolean }) => Promise<void>;
  onRunDryRun: (projectName: string) => Promise<void>;
};

export default function Projects({ projects, onCreateProject, onRunDryRun }: ProjectsProps) {
  return (
    <div className="stack">
      <ProjectForm onSubmit={onCreateProject} />
      <section className="card">
        <h2>Projetos</h2>
        {projects.length === 0 ? <p className="muted">Nenhum projeto encontrado.</p> : (
          <div className="project-list">
            {projects.map((project) => (
              <article key={project.database_id ?? project.name} className="project-item">
                <div><strong>{project.name}</strong><p className="muted">{project.template} · {project.workflow}</p></div>
                <button type="button" onClick={() => onRunDryRun(project.name)}>Executar dry-run</button>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
