type StatusBadgeProps = { status: string };

export default function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toLowerCase();
  return <span className={`status-badge status-${normalized}`}>{status}</span>;
}
