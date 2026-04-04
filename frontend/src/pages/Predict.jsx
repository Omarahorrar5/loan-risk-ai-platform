import { useState } from 'react';
import { predict } from '../api/client';
import ResultPanel from '../components/ResultPanel';

const DEFAULT_FORM = {
  person_age: '', person_income: '',
  person_home_ownership: 'RENT', person_emp_length: '',
  loan_intent: 'PERSONAL', loan_grade: 'C',
  loan_amnt: '', loan_int_rate: '',
  loan_percent_income: '', cb_person_default_on_file: 'N',
  cb_person_cred_hist_length: ''
};

const FIELDS = [
  { key: 'person_age',                 label: 'Age',                        type: 'number' },
  { key: 'person_income',              label: 'Annual Income ($)',           type: 'number' },
  { key: 'person_home_ownership',      label: 'Home Ownership',             type: 'select', opts: ['RENT','MORTGAGE','OWN','OTHER'] },
  { key: 'person_emp_length',          label: 'Employment Length (yrs)',     type: 'number', step: '0.5' },
  { key: 'loan_intent',                label: 'Loan Intent',                type: 'select', opts: ['PERSONAL','EDUCATION','MEDICAL','VENTURE','HOMEIMPROVEMENT','DEBTCONSOLIDATION'] },
  { key: 'loan_grade',                 label: 'Loan Grade',                 type: 'select', opts: ['A','B','C','D','E','F','G'] },
  { key: 'loan_amnt',                  label: 'Loan Amount ($)',            type: 'number' },
  { key: 'loan_int_rate',              label: 'Interest Rate (%)',          type: 'number', step: '0.1' },
  { key: 'loan_percent_income',        label: 'Loan / Income Ratio',        type: 'number', step: '0.01' },
  { key: 'cb_person_default_on_file',  label: 'Prior Default',             type: 'select', opts: ['N','Y'] },
  { key: 'cb_person_cred_hist_length', label: 'Credit History (yrs)',       type: 'number', span: 2 },
];

export default function Predict({ onNewPrediction }) {
  const [form,    setForm]    = useState(DEFAULT_FORM);
  const [result,  setResult]  = useState(null);
  const [lastForm,setLastForm]= useState({});
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  }

  async function handleSubmit() {
    setError(''); setLoading(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) =>
          ['person_age','person_income','person_emp_length','loan_amnt',
           'loan_int_rate','loan_percent_income','cb_person_cred_hist_length']
            .includes(k) ? [k, Number(v)] : [k, v]
        )
      );
      const { data } = await predict(payload);
      setResult(data);
      setLastForm({ ...form });
      onNewPrediction({ form: { ...form }, result: data });
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">
      <div className="page-title">Risk Assessment</div>
      <p className="page-sub">Submit applicant data to receive an instant credit risk prediction.</p>

      <div className="grid-2">
        <div className="card">
          <div className="card-label">Applicant Details</div>
          <div className="form-grid">
            {FIELDS.map(f => (
              <div className="field" key={f.key} style={f.span ? { gridColumn: `span ${f.span}` } : {}}>
                <label htmlFor={f.key}>{f.label}</label>
                {f.type === 'select' ? (
                  <select id={f.key} name={f.key} value={form[f.key]} onChange={handleChange}>
                    {f.opts.map(o => <option key={o}>{o}</option>)}
                  </select>
                ) : (
                  <input
                    id={f.key} name={f.key} type="number"
                    step={f.step ?? '1'} value={form[f.key]}
                    onChange={handleChange} placeholder="—"
                  />
                )}
              </div>
            ))}
          </div>
          <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Analyzing…' : 'Run Risk Assessment'}
          </button>
          {error && <div className="error-box">⚠ {error}</div>}
        </div>

        <ResultPanel result={result} formData={lastForm} />
      </div>
    </div>
  );
}