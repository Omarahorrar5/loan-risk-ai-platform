import './StatCard.css';

export default function StatCard({ label, value, color }) {
  return (
    <div className="stat-card card">
      <div className="card-label">{label}</div>
      <div className={`stat-value ${color ?? ''}`}>{value}</div>
    </div>
  );
}