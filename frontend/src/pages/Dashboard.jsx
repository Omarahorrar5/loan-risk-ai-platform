import { useEffect, useState } from 'react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, Cell, PieChart, Pie, Legend
} from 'recharts';
import { getMetrics, getHistory } from '../api/client';
import StatCard from '../components/StatCard';
import HistoryTable from '../components/HistoryTable';
import './Dashboard.css';

export default function Dashboard() {
  const [metrics, setMetrics] = useState({});
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchAll();
  }, []);

  async function fetchAll() {
    try {
      const [m, h] = await Promise.all([getMetrics(), getHistory()]);
      setMetrics(m.data);
      // normalize shape to match what charts + table expect
      setHistory(h.data.map(row => ({
        result: {
          risk_probability: row.risk_probability,
          decision:         row.decision,
        },
        form: row.form,
      })));
    } catch (e) {
      console.error('Dashboard fetch error:', e);
    }
  }

  const pieData = [
    { name: 'Safe',  value: metrics.safe  ?? 0 },
    { name: 'Risky', value: metrics.risky ?? 0 },
  ];

  const lineData = history.map((h, i) => ({
    name:        `#${i + 1}`,
    probability: +(h.result.risk_probability * 100).toFixed(1),
    decision:    h.result.decision,
  }));

  const riskyRate = metrics.risky_rate ?? 'N/A';
  const rateColor = riskyRate === 'N/A' ? 'muted'
    : parseFloat(riskyRate) > 50 ? 'risky' : 'safe';

  return (
    <div className="page-content">
      <div className="page-title">Dashboard</div>
      <p className="page-sub">All predictions — persisted across sessions.</p>

      <div className="grid-4">
        <StatCard label="Total Predictions" value={metrics.total_predictions ?? 0} color="purple" />
        <StatCard label="Safe"              value={metrics.safe  ?? 0}             color="safe"   />
        <StatCard label="Risky"             value={metrics.risky ?? 0}             color="risky"  />
        <StatCard label="Risky Rate"        value={riskyRate}                      color={rateColor} />
      </div>

      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        {/* PIE */}
        <div className="card">
          <div className="card-label">Safe vs Risky Distribution</div>
          {(metrics.total_predictions ?? 0) === 0
            ? <div className="dash-empty">No predictions yet.</div>
            : <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                       paddingAngle={3} dataKey="value">
                    <Cell fill="rgba(0,245,160,0.8)" stroke="#00f5a0" />
                    <Cell fill="rgba(255,63,94,0.8)" stroke="#ff3f5e" />
                  </Pie>
                  <Legend formatter={(v) => <span style={{ color: 'var(--text)', fontSize: '0.75rem' }}>{v}</span>} />
                  <Tooltip
                    contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8, fontFamily: 'var(--font-m)', fontSize: '0.78rem' }}
                    labelStyle={{ color: 'var(--text)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
          }
        </div>

        {/* LINE */}
        <div className="card">
          <div className="card-label">Risk Probability Over Time</div>
          {lineData.length === 0
            ? <div className="dash-empty">No predictions yet.</div>
            : <ResponsiveContainer width="100%" height={220}>
                <LineChart data={lineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="name" tick={{ fill: 'var(--muted)', fontSize: 10, fontFamily: 'var(--font-m)' }} />
                  <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`}
                         tick={{ fill: 'var(--muted)', fontSize: 10, fontFamily: 'var(--font-m)' }} />
                  <Tooltip
                    formatter={(v) => [`${v}%`, 'Risk']}
                    contentStyle={{ background: 'var(--surface2)', border: '1px solid var(--border)', borderRadius: 8, fontFamily: 'var(--font-m)', fontSize: '0.78rem' }}
                  />
                  <Line type="monotone" dataKey="probability" stroke="var(--purple)"
                        strokeWidth={2} dot={(props) => {
                          const { cx, cy, payload } = props;
                          const color = payload.decision === 'SAFE' ? '#00f5a0' : '#ff3f5e';
                          return <circle key={cx} cx={cx} cy={cy} r={5} fill={color} stroke={color} />;
                        }}
                  />
                </LineChart>
              </ResponsiveContainer>
          }
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.8rem' }}>
        <button onClick={fetchAll} style={{
          background: 'none', border: '1px solid var(--border)', color: 'var(--muted)',
          fontFamily: 'var(--font-m)', fontSize: '0.72rem', padding: '0.4rem 0.9rem',
          borderRadius: '6px', cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.08em'
        }}>
          ↻ Refresh
        </button>
      </div>

      <div className="card">
        <div className="card-label" style={{ marginBottom: '1rem' }}>Prediction Log</div>
        <HistoryTable history={history} />
      </div>
    </div>
  );
}