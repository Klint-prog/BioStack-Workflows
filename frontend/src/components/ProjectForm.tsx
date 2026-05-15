import { FormEvent, useMemo, useState } from 'react';

type ProjectFormProps = {
  onSubmit: (payload: { name: string; template: string; force: boolean }) => Promise<void>;
};

const templateDescriptions: Record<string, string> = {
  'rnaseq-basic': 'Estrutura demonstrativa para RNA-seq com dry-run auditável.',
  'variant-calling-basic': 'Estrutura demonstrativa para variant calling sem interpretação clínica.'
};

export default function ProjectForm({ onSubmit }: ProjectFormProps) {
  const [name, setName] = useState('demo-api');
  const [template, setTemplate] = useState('rnaseq-basic');
  const [force, setForce] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [touched, setTouched] = useState(false);

  const normalizedName = name.trim();
  const nameError = touched && normalizedName.length === 0 ? 'Informe um nome de projeto.' : '';
  const templateHelp = useMemo(() => templateDescriptions[template] ?? 'Template operacional disponível na API.', [template]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched(true);
    if (!normalizedName) return;

    setSubmitting(true);
    try {
      await onSubmit({ name: normalizedName, template, force });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card form" onSubmit={handleSubmit}>
      <div className="form-intro">
        <h2>Criar projeto operacional</h2>
        <p className="muted">O projeto será criado pela API e persistido no workspace compartilhado da plataforma.</p>
      </div>
      <label>
        Nome do projeto
        <input
          value={name}
          onBlur={() => setTouched(true)}
          onChange={(event) => setName(event.target.value)}
          aria-invalid={Boolean(nameError)}
          placeholder="ex.: rnaseq-cliente-a"
          required
        />
        {nameError ? <small className="field-error">{nameError}</small> : <small className="muted">Use nomes curtos, sem acentos e fáceis de auditar.</small>}
      </label>
      <label>
        Template
        <select value={template} onChange={(event) => setTemplate(event.target.value)}>
          <option value="rnaseq-basic">rnaseq-basic</option>
          <option value="variant-calling-basic">variant-calling-basic</option>
        </select>
        <small className="muted">{templateHelp}</small>
      </label>
      <label className="checkbox">
        <input type="checkbox" checked={force} onChange={(event) => setForce(event.target.checked)} />
        <span>Recriar se existir <small>Substitui a estrutura do projeto quando a API permitir.</small></span>
      </label>
      <button type="submit" disabled={submitting || !normalizedName}>{submitting ? 'Criando projeto...' : 'Criar projeto'}</button>
    </form>
  );
}
