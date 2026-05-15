import { FormEvent, useState } from 'react';

type ProjectFormProps = {
  onSubmit: (payload: { name: string; template: string; force: boolean }) => Promise<void>;
};

export default function ProjectForm({ onSubmit }: ProjectFormProps) {
  const [name, setName] = useState('demo-api');
  const [template, setTemplate] = useState('rnaseq-basic');
  const [force, setForce] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({ name, template, force });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card form" onSubmit={handleSubmit}>
      <label>Nome do projeto<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
      <label>Template<select value={template} onChange={(event) => setTemplate(event.target.value)}><option value="rnaseq-basic">rnaseq-basic</option><option value="variant-calling-basic">variant-calling-basic</option></select></label>
      <label className="checkbox"><input type="checkbox" checked={force} onChange={(event) => setForce(event.target.checked)} /> recriar se existir</label>
      <button type="submit" disabled={submitting}>{submitting ? 'Criando...' : 'Criar projeto'}</button>
    </form>
  );
}
