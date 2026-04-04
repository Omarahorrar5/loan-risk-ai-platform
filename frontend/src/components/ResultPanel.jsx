import ProbBar from './ProbBar';
import './ResultPanel.css';

export default function ResultPanel({ result, formData }) {
  if (!result) {
    return (
      <div className="card result-empty">
        <div className="empty-icon">◎</div>
        <p>Submit an applicant to see<br/>the risk assessment here.</p>
      </div>
    );
  }

  const isSafe = result.decision === 'SAFE';

  return (
    <div className={`card result-panel fade-up ${result.decision.toLowerCase()}`}>
      <div className="card-label">Assessment Result</div>

      <div className="result-main">
        <div className={`result-icon ${result.decision.toLowerCase()}`}>
          {isSafe ? '✓' : '✗'}
        </div>
        <div>
          <div className={`result-decision ${result.decision.toLowerCase()}`}>
            {result.decision}
          </div>
          <div className="result-sub">
            {(result.risk_probability * 100).toFixed(1)}% risk probability
            &nbsp;·&nbsp; threshold {(result.threshold * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      <ProbBar probability={result.risk_probability} decision={result.decision} />

      <div className="result-meta">
        <div className="meta-chip">
          <span className="card-label" style={{marginBottom:0}}>Age / Income</span>
          <span>{formData.person_age}y · ${formData.person_income?.toLocaleString()}</span>
        </div>
        <div className="meta-chip">
          <span className="card-label" style={{marginBottom:0}}>Loan</span>
          <span>${formData.loan_amnt?.toLocaleString()} · Grade {formData.loan_grade}</span>
        </div>
        <div className="meta-chip">
          <span className="card-label" style={{marginBottom:0}}>Intent</span>
          <span>{formData.loan_intent}</span>
        </div>
        <div className="meta-chip">
          <span className="card-label" style={{marginBottom:0}}>Prior Default</span>
          <span>{formData.cb_person_default_on_file === 'Y' ? 'Yes' : 'No'}</span>
        </div>
      </div>
    </div>
  );
}