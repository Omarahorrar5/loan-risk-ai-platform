import './HistoryTable.css';

export default function HistoryTable({ history }) {
  if (history.length === 0) {
    return <div className="empty-table">No predictions recorded yet.</div>;
  }

  return (
    <div className="table-wrap">
      <table className="h-table">
        <thead>
          <tr>
            {['#','Age','Income','Grade','Amount','Intent','Probability','Decision']
              .map(h => <th key={h}>{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {[...history].reverse().map((h, i) => (
            <tr key={i}>
              <td className="muted">{history.length - i}</td>
              <td>{h.form.person_age}</td>
              <td>${h.form.person_income?.toLocaleString()}</td>
              <td>{h.form.loan_grade}</td>
              <td>${h.form.loan_amnt?.toLocaleString()}</td>
              <td className="muted">{h.form.loan_intent}</td>
              <td>
                <div className="mini-bar-wrap">
                  <div className="mini-bar-track">
                    <div
                      className={`mini-bar-fill ${h.result.decision.toLowerCase()}`}
                      style={{ width: `${(h.result.risk_probability * 100).toFixed(1)}%` }}
                    />
                  </div>
                  <span>{(h.result.risk_probability * 100).toFixed(1)}%</span>
                </div>
              </td>
              <td>
                <span className={`badge ${h.result.decision.toLowerCase()}`}>
                  {h.result.decision}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}