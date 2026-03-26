import React, { useState } from 'react';
import { API_BASE } from './config';

const initial = {
  brand: '',
  model: '',
  cpu: '',
  ram_gb: '16',
  storage_gb: '512',
  storage_type: 'SSD',
  gpu_type: 'integrated',
  age_years: '',
  condition: '',
};

export default function FmvEstimator() {
  const [form, setForm] = useState(initial);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = (key, value) => {
    setForm((f) => ({ ...f, [key]: value }));
    setError(null);
    setResult(null);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const body = {
      brand: form.brand.trim(),
      model: form.model.trim(),
      cpu: form.cpu.trim(),
      ram_gb: parseInt(form.ram_gb, 10),
      storage_gb: parseInt(form.storage_gb, 10),
      storage_type: form.storage_type,
      gpu_type: form.gpu_type,
    };

    if (form.age_years.trim() !== '') {
      body.age_years = parseFloat(form.age_years);
    }
    if (form.condition.trim() !== '') {
      body.condition = form.condition.trim();
    }

    try {
      const res = await fetch(`${API_BASE}/api/fmv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.error || 'Request failed');
        return;
      }
      setResult(data);
    } catch {
      setError('Could not reach the server. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="how-section-box fmv-estimator-box">
      <h2>Laptop estimate</h2>
      <p className="fmv-estimator-lead">
        Enter specs for a model-based fair market value (new) and an optional used-price
        estimate.
      </p>
      <form onSubmit={onSubmit}>
        <div className="form-group form-full">
          <label>Brand</label>
          <input
            value={form.brand}
            onChange={(e) => update('brand', e.target.value)}
            placeholder="e.g. Dell"
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Model</label>
            <input
              value={form.model}
              onChange={(e) => update('model', e.target.value)}
              placeholder="e.g. Latitude 5420"
              required
            />
          </div>
          <div className="form-group">
            <label>CPU</label>
            <input
              value={form.cpu}
              onChange={(e) => update('cpu', e.target.value)}
              placeholder="e.g. i7-1165G7"
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>RAM (GB)</label>
            <input
              type="number"
              min="1"
              value={form.ram_gb}
              onChange={(e) => update('ram_gb', e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Storage (GB)</label>
            <input
              type="number"
              min="1"
              value={form.storage_gb}
              onChange={(e) => update('storage_gb', e.target.value)}
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Storage type</label>
            <select
              value={form.storage_type}
              onChange={(e) => update('storage_type', e.target.value)}
            >
              <option value="SSD">SSD</option>
              <option value="HDD">HDD</option>
            </select>
          </div>
          <div className="form-group">
            <label>GPU</label>
            <select value={form.gpu_type} onChange={(e) => update('gpu_type', e.target.value)}>
              <option value="integrated">Integrated</option>
              <option value="dedicated">Dedicated</option>
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Age (years, optional)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              value={form.age_years}
              onChange={(e) => update('age_years', e.target.value)}
              placeholder="e.g. 2"
            />
          </div>
          <div className="form-group">
            <label>Condition (optional)</label>
            <input
              value={form.condition}
              onChange={(e) => update('condition', e.target.value)}
              placeholder="e.g. good, fair"
            />
          </div>
        </div>
        <div className="form-actions fmv-form-actions">
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Estimating…' : 'Get estimate'}
          </button>
        </div>
      </form>
      {error && (
        <p className="fmv-error" role="alert">
          {error}
        </p>
      )}
      {result && (
        <div className="fmv-result">
          <h3>Results (SGD)</h3>
          <p className="fmv-result-fmv">FMV (new): S${Number(result.fmv_sgd).toFixed(2)}</p>
          <p className="fmv-result-used">Used estimate: S${Number(result.used_sgd).toFixed(2)}</p>
          {result.device && (
            <p className="fmv-result-device">
              {result.device.brand} {result.device.model} · {result.device.cpu} ·{' '}
              {result.device.ram_gb} GB RAM · {result.device.storage_gb} GB {result.device.storage_type}{' '}
              · {result.device.gpu_type} GPU
            </p>
          )}
        </div>
      )}
    </div>
  );
}
