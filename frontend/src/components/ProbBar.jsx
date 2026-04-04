import './ProbBar.css';

export default function ProbBar({ probability, decision }) {
  const pct = (probability * 100).toFixed(1);
  return (
    <div className="prob-bar-wrap">
      <div className="prob-bar-labels">
        <span>0%</span>
        <span className="prob-center">Risk — {pct}%</span>
        <span>100%</span>
      </div>
      <div className="prob-bar-track">
        <div
          className={`prob-bar-fill ${decision.toLowerCase()}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}