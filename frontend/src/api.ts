import { EarthdataStatus, DatasetInfo, AnalysisMetrics, GranuleMetadata, CaseStudy } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export async function fetchHealth(): Promise<{ status: string; earthdata_configured: boolean; demo_scenes_ready: boolean }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch health');
  return res.json();
}

export async function fetchReadiness(): Promise<any> {
  const res = await fetch(`${API_BASE}/readiness`);
  return res.json();
}

export async function fetchEarthdataStatus(): Promise<EarthdataStatus> {
  const res = await fetch(`${API_BASE}/nasa/status`);
  if (!res.ok) throw new Error('Failed to fetch Earthdata status');
  return res.json();
}

export async function fetchDatasets(): Promise<DatasetInfo[]> {
  const res = await fetch(`${API_BASE}/nasa/datasets`);
  if (!res.ok) throw new Error('Failed to fetch datasets');
  return res.json();
}

export async function fetchCases(): Promise<CaseStudy[]> {
  const res = await fetch(`${API_BASE}/analysis/cases`);
  if (!res.ok) throw new Error('Failed to fetch demonstration cases');
  return res.json();
}

export async function searchGranules(
  dataset: string,
  bbox: number[],
  startDate: string,
  endDate: string
): Promise<{ granules: GranuleMetadata[]; provenance: string }> {
  const res = await fetch(`${API_BASE}/nasa/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset,
      bbox,
      start_date: startDate,
      end_date: endDate,
      limit: 10
    })
  });
  if (!res.ok) throw new Error('Search failed');
  return res.json();
}

export async function runProcess(
  caseId: string = 'chennai_live_case',
  thresholds?: { darkening?: number; brightening?: number }
): Promise<AnalysisMetrics> {
  const body: any = { case_id: caseId };
  if (thresholds?.darkening !== undefined) body.darkening_threshold_db = thresholds.darkening;
  if (thresholds?.brightening !== undefined) body.brightening_threshold_db = thresholds.brightening;

  const res = await fetch(`${API_BASE}/nasa/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error('Processing failed');
  return res.json();
}

export async function compareAnalysis(caseId: string = 'chennai_live_case'): Promise<any> {
  const res = await fetch(`${API_BASE}/analysis/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId })
  });
  if (!res.ok) throw new Error('Comparison failed');
  return res.json();
}

export async function fetchMetrics(analysisId: string): Promise<AnalysisMetrics> {
  const res = await fetch(`${API_BASE}/analysis/${analysisId}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
}

export async function fetchResults(analysisId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/analysis/${analysisId}/results`);
  if (!res.ok) throw new Error('Failed to fetch results');
  return res.json();
}
