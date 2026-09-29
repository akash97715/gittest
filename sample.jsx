import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useMsal } from '@azure/msal-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts';
import {
  Layers, FileText, Users, GraduationCap, AlertTriangle,
  ChevronDown, Info, Activity, Target, Sparkles, CheckCircle2, Calendar,
  ArrowUpRight, X, MapPin, Clock, Briefcase, Grid3x3, RotateCcw, Leaf, Building2, User, Filter, Map as MapIcon,
  Lock,
} from 'lucide-react';
import TrainingSkillGapsView, { RepFcrDrilldown } from './TrainingSkillGapsView';
import SkillProficiencyTrendView from './SkillProficiencyTrendView';
import { FCRDetailPanel } from './FCRsPage';
import { telemetry } from '../utils/telemetryClient';
import { getViewAsScope } from '../utils/viewAs';
import AIDigestButton from '../components/AIDigestButton';
import AIDigestPanel from '../components/AIDigestPanel';

// ── Static fallback chart data (shown while loading) ──────────
const fcrByRegion = [
  { region: 'Northeast', count: 0 },
  { region: 'Southeast', count: 0 },
  { region: 'Central',   count: 0 },
  { region: 'West',      count: 0 },
];

const completionTrend = [
  { quarter: '—', total_fcrs: 0, coached: 0, repeats: 0, required_fcrs: 0, coverage: 0 },
];

// ── Filter options ─────────────────────────────────────────────
const TIMEFRAME_OPTIONS = [
  { label: 'All time',      value: null },
  { label: 'Past 7 days',   value: '7' },
  { label: 'Past 30 days',  value: '30' },
  { label: 'Past quarter',  value: '90' },
  { label: 'Past 6 months', value: '180' },
  { label: 'Past year',     value: '365' },
  { label: 'Custom range',  value: 'custom' },
];

const TA_OPTIONS = [
  { label: 'All TAs',              value: null },
  { label: 'Immunology (IMM)',     value: 'IMM' },
  { label: 'Oncology (ONC)',       value: 'ONC' },
  { label: 'Neuroscience (NS)',    value: 'NS' },
  { label: 'Specialty Care (SCG)', value: 'SCG' },
];

// Client-side mirror of server.js's TA_GROUP_TO_FRANS, used only to clear a
// selected Disease Area that no longer belongs to a newly selected TA (the
// dropdown OPTIONS themselves still come from /api/filters/disease-areas).
const TA_GROUP_TO_FRANS = {
  IMM: ['Autoantibody-Neuroimmunology', 'Autoantibody - Pipeline', 'Gastroenterology', 'Rheumatology', 'Dermatology'],
  ONC: ['Oncology Head & Neck Cancer MSLs', 'ONC - Hematology', 'GU', 'Lung'],
  NS:  ['CAPLYTA MSLs', 'SCZ', 'Mood'],
  SCG: ['Real World Value & Evidence Field'],
};

const REGION_OPTIONS = [
  { label: 'All regions', value: null },
  { label: 'West',        value: 'West' },
  { label: 'Central',     value: 'Central' },
  { label: 'Northeast',   value: 'Northeast' },
  { label: 'Southeast',   value: 'Southeast' },
  { label: 'East',        value: 'East' },
];

const SUMMARY_FILTER_EVENT_NAMES = {
  timeframe: { all: 'summary_filter_timeframe_all_time', 7: 'summary_filter_timeframe_7d', 30: 'summary_filter_timeframe_30d', 90: 'summary_filter_timeframe_quarter', 180: 'summary_filter_timeframe_6m', 365: 'summary_filter_timeframe_365d', custom: 'summary_filter_timeframe_custom_opened' },
  'therapeutic-area': { all: 'summary_filter_ta_all', IMM: 'summary_filter_ta_imm', ONC: 'summary_filter_ta_onc', NS: 'summary_filter_ta_ns', SCG: 'summary_filter_ta_scg' },
  region: { all: 'summary_filter_region_all', West: 'summary_filter_region_west', Central: 'summary_filter_region_central', Northeast: 'summary_filter_region_northeast', Southeast: 'summary_filter_region_southeast', East: 'summary_filter_region_east' },
};

const SUMMARY_FILTER_OPEN_EVENT_NAMES = {
  timeframe: 'summary_filter_timeframe_opened',
  ta: 'summary_filter_ta_opened',
  region: 'summary_filter_region_opened',
};

// ── KPI Tile ───────────────────────────────────────────────────
const ACCENT_MAP = {
  red:   { iconBg: '#FDECEC', iconColor: '#D71600', Icon: FileText      },
  green: { iconBg: '#DCFCE7', iconColor: '#15803D', Icon: Users         },
  amber: { iconBg: '#FEF9C3', iconColor: '#A16207', Icon: GraduationCap },
  redhl: { iconBg: '#FDECEC', iconColor: '#D71600', Icon: AlertTriangle },
};

function KpiTile({ label, tag, value, valueSuffix, sub, accent, highlighted }) {
  const { iconBg, iconColor, Icon } = ACCENT_MAP[accent] || ACCENT_MAP.red;
  return (
    <div
      className="kpi-tile"
      style={{
        background:   highlighted ? '#FDECEC' : '#fff',
        border:       highlighted ? '1.5px solid #D71600' : '1px solid #EEE7E8',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="kpi-label">{label}</div>
          <div className="kpi-tag"><Calendar size={10} style={{ verticalAlign: '-1px', marginRight: 3 }} />{tag}</div>
        </div>
        <div style={{ width: 30, height: 30, borderRadius: 8, background: iconBg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Icon size={15} color={iconColor} />
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, margin: '8px 0 4px' }}>
        <span style={{ fontSize: 28, fontWeight: 800, lineHeight: 1, color: highlighted ? '#D71600' : '#1A1A1A' }}>{value}</span>
        {valueSuffix && <span style={{ fontSize: 16, color: '#9CA3AF', fontWeight: 500 }}>{valueSuffix}</span>}
      </div>
      <div className="kpi-sub">{sub}</div>
    </div>
  );
}

// ── View Selector Card ─────────────────────────────────────────
function ViewCard({ num, icon: Icon, title, sub, active, onClick }) {
  return (
    <div
      className="view-card"
      onClick={onClick}
      role="button"
      aria-pressed={active}
      style={{
        border:     active ? '2px solid #D71600' : '1.5px solid #EEE7E8',
        background: active ? '#FDECEC' : '#fff',
        display: 'flex', alignItems: 'center', gap: 10,
      }}
    >
      <div style={{
        width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
        background: active ? '#D71600' : '#F3F4F6',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={14} color={active ? '#fff' : '#9CA3AF'} />
      </div>
      <span style={{ fontSize: 9, fontWeight: 700, color: active ? '#D71600' : '#9CA3AF', flexShrink: 0 }}>
        {String(num).padStart(2, '0')}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: '#1A1A1A', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{title}</div>
        <div style={{ fontSize: 10, color: '#6B7280', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{sub}</div>
      </div>
      {active
        ? <span className="live-pill" style={{ flexShrink: 0 }}><span className="live-dot" />LIVE</span>
        : <ChevronDown size={12} color="#9CA3AF" style={{ transform: 'rotate(-90deg)', flexShrink: 0 }} />
      }
    </div>
  );
}

// ── Tooltips ───────────────────────────────────────────────────
const BarTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const fullName  = payload[0]?.payload?.fullName;
  const fieldHead = payload[0]?.payload?.fieldHead;
  return (
    <div className="chart-tip">
      <div className="chart-tip-label">{fullName || label}</div>
      <div style={{ color: '#D71600', fontWeight: 600 }}>{payload[0].value} FCRs</div>
      {fieldHead && (
        <div style={{ marginTop: 4, paddingTop: 4, borderTop: '1px solid #F3F4F6', fontSize: 10, color: '#6B7280' }}>
          <div style={{ fontWeight: 700, color: '#1B1F2A' }}>{fieldHead.name}</div>
          <div>{fieldHead.title}</div>
        </div>
      )}
    </div>
  );
};

// Computes a "zoomed-in" Y-axis domain/ticks from the actual data range
// (plus any reference values that must stay visible, e.g. the required-base
// line), so bars aren't dwarfed by a fixed/oversized ceiling — same approach
// used for the Skill Proficiency Trend charts' Y-axis.
function getCountAxis(values) {
  const nums = (values || []).filter(v => typeof v === 'number' && !Number.isNaN(v));
  const rawMax = nums.length ? Math.max(...nums, 0) : 0;
  if (rawMax <= 0) return { domain: [0, 'dataMax'], ticks: undefined };
  const max = Math.ceil((rawMax * 1.15) / 5) * 5 || 5;
  const step = max / 4;
  const niceStep = Math.ceil(step / 5) * 5 || step;
  const niceMax = niceStep * 4;
  const ticks = Array.from({ length: 5 }, (_, i) => Math.round(niceStep * i));
  return { domain: [0, niceMax], ticks };
}

// Custom X-axis tick for the coverage chart — shows the quarter name plus
// its coverage % underneath (coached ÷ required base), so gaps are visible
// at a glance without hovering.
function CoverageAxisTick({ x, y, payload, data }) {
  const item = (data || []).find(d => d.quarter === payload.value);
  const coverage = item?.coverage;
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={12} textAnchor="middle" fontSize={12} fill="#6B7280">{payload.value}</text>
      {coverage != null && (
        <text x={0} y={0} dy={25} textAnchor="middle" fontSize={9} fontWeight={700} fill={coverage >= 100 ? '#15803D' : coverage >= 70 ? '#D97706' : '#DC2626'}>
          {coverage}% coverage
        </text>
      )}
    </g>
  );
}

// Enhanced tooltip for the coverage chart — total FCRs, coached vs required
// (with %), repeat observations, and a clear "gap" or "fully covered" status.
const CoverageTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  const gap = Math.max(d.required_fcrs - d.coached, 0);
  return (
    <div className="chart-tip">
      <div className="chart-tip-label">{label}</div>
      <div style={{ color: '#1B1F2A', fontWeight: 600 }}>FCRs completed: {d.total_fcrs}</div>
      <div style={{ color: '#D71600', fontWeight: 600, marginTop: 2 }}>
        MSLs coached: {d.coached} of {d.required_fcrs} <span style={{ color: '#6B7280', fontWeight: 400 }}>({d.coverage}%)</span>
      </div>
      <div style={{ color: '#6B7280', marginTop: 2 }}>Repeat observations: {d.repeats}</div>
      <div style={{ marginTop: 4, paddingTop: 4, borderTop: '1px solid #F3F4F6', fontSize: 10, fontWeight: 700, color: gap > 0 ? '#DC2626' : '#15803D' }}>
        {gap > 0 ? `${gap} MSL${gap === 1 ? '' : 's'} with no FCR` : '✓ Every MSL coached'}
      </div>
    </div>
  );
};

// Custom X-axis tick for the drill-down chart — shows the disease-area name
// plus the field head's name underneath (when known), so it's visible at a
// glance without needing to hover.
function DiseaseAxisTick({ x, y, payload, data }) {
  const item = (data || []).find(d => d.region === payload.value);
  const headName = item?.fieldHead?.name;
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={12} textAnchor="middle" fontSize={11} fill="#6B7280">{payload.value}</text>
      {headName && (
        <text x={0} y={0} dy={25} textAnchor="middle" fontSize={9} fontWeight={600} fill="#9CA3AF">{headName}</text>
      )}
    </g>
  );
}

// Custom X-axis tick for the Field-Director drill-down (level 3) — shows the
// region name (derived server-side from the FD's own org node) plus the real
// Field Director's name underneath, from live org.hierarchy + Redshift data.
function FDAxisTick({ x, y, payload, data }) {
  const item = (data || []).find(d => d.region === payload.value);
  const fdName = item?.fd_name;
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={12} textAnchor="middle" fontSize={11} fill="#6B7280">{payload.value}</text>
      {fdName && (
        <text x={0} y={0} dy={25} textAnchor="middle" fontSize={9} fontWeight={600} fill="#9CA3AF">{fdName}</text>
      )}
    </g>
  );
}

const FDBarTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  return (
    <div className="chart-tip">
      <div className="chart-tip-label">{label}</div>
      <div style={{ color: '#D71600', fontWeight: 600 }}>{payload[0].value} FCRs</div>
      {item?.fd_name && (
        <div style={{ marginTop: 4, paddingTop: 4, borderTop: '1px solid #F3F4F6', fontSize: 10, color: '#6B7280' }}>
          <div style={{ fontWeight: 700, color: '#1B1F2A' }}>{item.fd_name}</div>
          <div>Field Director{item.vacant_count ? ` · ${item.vacant_count} vacant territor${item.vacant_count === 1 ? 'y' : 'ies'}` : ''}</div>
        </div>
      )}
    </div>
  );
};

// Level-4 drill-down: the MSL roster for one Field Director, each card
// showing real FCR counts pulled live from Redshift (org.hierarchy for the
// roster itself). Clicking a (non-vacant) rep opens their FCR list, same
// "click rep -> pick FCR -> open it" flow used in Training & Skill Gaps.
function MslTeamList({ reps, loading, onSelectRep }) {
  if (loading) {
    return <div style={{ padding: '60px 0', textAlign: 'center', color: '#9CA3AF', fontSize: 13 }}>Loading MSL team…</div>;
  }
  if (!reps.length) {
    return <div style={{ padding: '60px 0', textAlign: 'center', color: '#9CA3AF', fontSize: 13 }}>No MSLs found for this Field Director.</div>;
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 315, overflowY: 'auto', paddingRight: 4 }}>
      {reps.map((r, i) => (
        <div
          key={r.wwid || i}
          onClick={r.is_vacant ? undefined : () => onSelectRep?.(r)}
          title={r.is_vacant ? undefined : `View ${r.name}'s FCRs`}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10,
            padding: '10px 12px', border: '1px solid #EEE7E8', borderRadius: 10,
            background: r.is_vacant ? '#FAFAFA' : '#fff',
            cursor: r.is_vacant ? 'default' : 'pointer',
          }}
        >
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: r.is_vacant ? '#9CA3AF' : '#1A1A1A' }}>
              {r.is_vacant ? 'Vacant Territory' : r.name}
            </div>
            <div style={{ fontSize: 11, color: '#6B7280', marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {[r.job_title, r.territory].filter(Boolean).join(' · ')}
            </div>
          </div>
          {!r.is_vacant && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 16, fontWeight: 800, color: '#D71600' }}>{r.fcr_count}</div>
                <div style={{ fontSize: 9, color: '#9CA3AF', fontWeight: 600 }}>FCR{r.fcr_count === 1 ? '' : 's'}</div>
              </div>
              <ArrowUpRight size={14} color="#C9CDD4" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── "More filters" FCR list panel (2026-09-08 bug fix) ──────────────────
// Generic, reusable side panel: given a set of query params (the SAME
// params used to filter the hero KPI cards — see buildActiveFilterParams
// below), fetches the matching FCRs from /api/fcrs and lists them, each
// row clickable to open the full FCR detail (reuses the app-level
// onOpenFcr flow already wired through App.jsx -> FCRsPage).
// Fixes:
//   Bug 1 (MSL filter): selecting an MSL and opening this panel always
//     shows that MSL's real FCR list/count, including "0 FCRs" when empty
//     — never substitutes Disease Area/TA data.
//   Bug 2 (Region filter): selecting a Region and opening this panel shows
//     the FCRs published in that region, each clickable to open.
//   Bug 3 (2026-09-08): "Open FCR" used to navigate away to the FCRs page.
//     It now opens the full FCRDetailPanel in-place (same pattern as
//     RepFcrDrilldown), so the user never leaves the Dashboard.
function FilteredFcrListPanel({ title, subtitle, queryParams, onClose }) {
  const [fcrs, setFcrs]       = useState([]);
  const [total, setTotal]     = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  const [openedFcr, setOpenedFcr]               = useState(null);
  const [fcrDetail, setFcrDetail]               = useState([]);
  const [fcrDetailLoading, setFcrDetailLoading] = useState(false);
  const [fcrDetailError, setFcrDetailError]     = useState(null);
  const [repTrend, setRepTrend]                 = useState([]);
  const [repTrendLoading, setRepTrendLoading]   = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const p = new URLSearchParams(queryParams);
    p.set('limit', '50');
    fetch(`/api/fcrs?${p}`)
      .then(r => r.json())
      .then(d => {
        if (d.error) throw new Error(d.error);
        setFcrs(d.rows || []);
        setTotal(d.total ?? (d.rows || []).length);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [JSON.stringify(queryParams)]);

  useEffect(() => {
    if (!openedFcr) return;
    setFcrDetail([]);
    setFcrDetailError(null);
    setFcrDetailLoading(true);
    setRepTrend([]);
    setRepTrendLoading(true);

    fetch(`/api/fcr/${encodeURIComponent(openedFcr.fcr_id)}`)
      .then(r => r.json())
      .then(d => { if (d.error) throw new Error(d.error); setFcrDetail(Array.isArray(d) ? d : []); })
      .catch(e => setFcrDetailError(e.message))
      .finally(() => setFcrDetailLoading(false));

    fetch(`/api/rep-trend/${encodeURIComponent(openedFcr.coachee_wwid)}`)
      .then(r => r.json())
      .then(d => setRepTrend(Array.isArray(d) ? d : []))
      .catch(() => {})
      .finally(() => setRepTrendLoading(false));
  }, [openedFcr]);

  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = prev; };
  }, []);

  const STATUS_COLOR = {
    Submitted: { bg: '#F0FDF4', color: '#15803D', border: '#BBF7D0' },
    Draft:     { bg: '#FFFBEB', color: '#A16207', border: '#FDE68A' },
    'Late Submission': { bg: '#FEF2F2', color: '#DC2626', border: '#FECACA' },
  };
  const fmtDate = v => v ? new Date(v).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—';

  return createPortal(
    <>
      {!openedFcr && (
      <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.18)', zIndex: 999 }} />
      <div style={{
        position: 'fixed', right: 0, top: 0, bottom: 0, width: 440,
        background: '#fff', zIndex: 1000, boxShadow: '-6px 0 32px rgba(0,0,0,0.14)',
        display: 'flex', flexDirection: 'column', animation: 'slideInRight 0.22s ease both',
      }}>
        <div style={{ padding: '20px 20px 16px', borderBottom: '1px solid #E9E5E7', background: 'linear-gradient(135deg, #1B1F2A 0%, #2A2F3D 100%)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 16, fontWeight: 800, color: '#fff' }}>{title}</div>
              {subtitle && <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.65)', marginTop: 2 }}>{subtitle}</div>}
            </div>
            <button onClick={onClose} style={{ border: 'none', background: 'rgba(255,255,255,0.1)', cursor: 'pointer', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, borderRadius: 6, flexShrink: 0 }}>
              <X size={15} />
            </button>
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: '#fff', background: 'rgba(215,22,0,0.35)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: 20, padding: '3px 10px' }}>
              {loading ? '…' : total} FCR{total === 1 ? '' : 's'}
            </span>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: 16, background: '#FAFAFA' }}>
          {loading && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, padding: '60px 0' }}>
              <div style={{ width: 30, height: 30, border: '3px solid #D71600', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
              <div style={{ fontSize: 12, color: '#9CA3AF' }}>Loading FCRs…</div>
            </div>
          )}
          {error && <div style={{ padding: 16, background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 10, color: '#991B1B', fontSize: 12 }}>{error}</div>}
          {/* Explicit "0 FCRs" empty state — never falls back to any other field (TA/Disease Area, etc.) */}
          {!loading && !error && fcrs.length === 0 && (
            <div style={{ textAlign: 'center', padding: 40, color: '#9CA3AF', fontSize: 12 }}>0 FCRs found for this selection.</div>
          )}
          {!loading && !error && fcrs.map(f => {
            const sc = STATUS_COLOR[f.status] || { bg: '#F3F0F1', color: '#6B7280', border: '#E9E5E7' };
            const coacheeName = [f.coachee_first, f.coachee_last].filter(Boolean).join(' ') || f.coachee_wwid || '—';
            return (
              <div key={f.fcr_id} style={{ background: '#fff', border: '1px solid #E9E5E7', borderRadius: 12, padding: 14, marginBottom: 10, boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Calendar size={12} color="#9CA3AF" />
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#1B1F2A' }}>{fmtDate(f.coaching_date)}</span>
                  </div>
                  <span style={{ fontSize: 10, fontWeight: 700, color: sc.color, background: sc.bg, border: `1px solid ${sc.border}`, borderRadius: 20, padding: '2px 9px' }}>{f.status}</span>
                </div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#1A1A1A', marginBottom: 8 }}>{coacheeName}</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 10px', marginBottom: 12, fontSize: 11 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#6B7280', overflow: 'hidden' }}>
                    <FileText size={11} color="#C9CDD4" style={{ flexShrink: 0 }} />
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{f.ta || '—'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#6B7280', overflow: 'hidden' }}>
                    <MapPin size={11} color="#C9CDD4" style={{ flexShrink: 0 }} />
                    <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{f.region || f.territory || f.district || '—'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#6B7280' }}>
                    <Clock size={11} color="#C9CDD4" style={{ flexShrink: 0 }} />
                    <span>{f.session_duration || '—'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: '#6B7280' }}>
                    <span>{f.days_since_coaching != null ? `${f.days_since_coaching}d ago` : '—'}</span>
                  </div>
                </div>
                <button
                  onClick={() => setOpenedFcr(f)}
                  style={{
                    width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                    padding: '7px 0', fontSize: 11, fontWeight: 700, color: '#fff',
                    border: 'none', borderRadius: 8, background: '#D71600', cursor: 'pointer',
                  }}
                >
                  Open FCR <ArrowUpRight size={12} color="#fff" />
                </button>
              </div>
            );
          })}
        </div>
      </div>
      </>
      )}

      {openedFcr && !fcrDetailLoading && !fcrDetailError && fcrDetail.length > 0 && (
        <FCRDetailPanel
          fcr={openedFcr}
          detail={fcrDetail}
          trend={repTrend}
          trendLoading={repTrendLoading}
          onClose={() => setOpenedFcr(null)}
        />
      )}
      {openedFcr && (fcrDetailLoading || fcrDetailError) && (
        <>
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', zIndex: 1010 }} />
          <div style={{
            position: 'fixed', top: 0, right: 0, height: '100vh', width: 540, zIndex: 1011,
            background: '#fff', boxShadow: '-8px 0 32px rgba(0,0,0,0.16)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12,
          }}>
            {fcrDetailLoading ? (
              <>
                <div style={{ width: 36, height: 36, border: '3px solid #D71600', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                <div style={{ fontSize: 13, color: '#6B7280' }}>Loading FCR…</div>
              </>
            ) : (
              <div style={{ padding: 24, textAlign: 'center' }}>
                <div style={{ fontSize: 13, color: '#991B1B', marginBottom: 12 }}>{fcrDetailError}</div>
                <button onClick={() => setOpenedFcr(null)} style={{ fontSize: 12, color: '#6B7280', background: 'none', border: '1px solid #E9E5E7', borderRadius: 8, padding: '6px 14px', cursor: 'pointer' }}>Back</button>
              </div>
            )}
          </div>
        </>
      )}
    </>,
    document.body
  );
}


// ── Filter Dropdown ────────────────────────────────────────────
// Option list is capped to ~5 visible rows (maxHeight) and scrolls for
// longer lists (MSL/Field Director/Job Role/Territory can have 50-800+
// options) so it never stretches the page's scrollable height. `extra`
// (e.g. the custom date-range picker) renders OUTSIDE the scroll area so
// it's always fully visible.
function FilterDropdown({ id, label, options, value, onChange, open, onToggle, extra, disabled, icon: IconComponent }) {
  const selected = options.find(o => o.value === value);
  const isActive = value !== null;
  const displayLabel = isActive ? selected?.label ?? label : label;

  // Locked by an active RBAC "View As" scope (see viewAsScope in
  // DashboardPage below) — render as a static, non-interactive pill instead
  // of a clickable dropdown so a locked Field Head can't widen their own
  // scope from the UI (the backend enforces this regardless, but the UI
  // should reflect it too).
  if (disabled) {
    return (
      <div
        className="filter-pill"
        title="Locked by your current role"
        style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: '#F3F4F6', color: '#6B7280', borderColor: '#E5E7EB', cursor: 'not-allowed' }}
      >
        <Lock size={11} color="#D71600" style={{ flexShrink: 0 }} /> {displayLabel}
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="filter-pill"
        onClick={() => {
          if (!open && SUMMARY_FILTER_OPEN_EVENT_NAMES[id]) {
            telemetry.trackCustomEvent(SUMMARY_FILTER_OPEN_EVENT_NAMES[id], {
              page: 'summary', filter: id, currentValue: value ?? 'all',
            });
          }
          onToggle(open ? null : id);
        }}
        style={isActive ? { background: '#D71600', color: '#fff', borderColor: '#D71600', fontWeight: 600 } : {}}
      >
        {IconComponent && <IconComponent size={14} style={{ marginRight: 4 }} />}
        {displayLabel}
        {isActive
          ? <span onMouseDown={e => {
              e.stopPropagation();
              telemetry.trackCustomEvent('summary_filter_cleared_single', {
                page: 'summary', filter: id, clearedValue: value,
              });
              onChange(null);
              onToggle(null);
            }} style={{ marginLeft: 5, opacity: 0.8, fontSize: 14, lineHeight: 1 }}>×</span>
          : <ChevronDown size={11} color="#9CA3AF" style={{ marginLeft: 4 }} />
        }
      </button>
      {open && (
        <div className="filter-dropdown-menu" style={{
          position: 'absolute', top: 'calc(100% + 6px)', left: 0, zIndex: 200,
          background: '#fff', border: '1px solid #E9E5E7', borderRadius: 12,
          boxShadow: '0 8px 28px rgba(0,0,0,0.13)', minWidth: 190,
        }}>
          <div
            className="filter-dropdown-list"
            role="listbox"
            tabIndex={-1}
            style={{ maxHeight: 220, overflowY: 'auto', overscrollBehavior: 'contain' }}
          >
            {options.map(opt => (
              <button
                key={String(opt.value)}
                role="option"
                aria-selected={opt.value === value}
                onMouseDown={() => { onChange(opt.value); if (opt.value !== 'custom') onToggle(null); }}
                style={{
                  display: 'block', width: '100%', textAlign: 'left',
                  padding: '9px 16px', fontSize: 13,
                  fontWeight: opt.value === value ? 700 : 400,
                  color: opt.value === value ? '#D71600' : '#1B1F2A',
                  background: opt.value === value ? '#FFF0F0' : 'transparent',
                  border: 'none', cursor: 'pointer',
                }}
              >
                {opt.value === value ? '✓ ' : '   '}{opt.label}
              </button>
            ))}
          </div>
          {extra}
        </div>
      )}
    </div>
  );
}

// ── Franchise/brand team name (fran_nm) → therapeutic area bucket ──
// NOTE: best-effort mapping based on typical J&J Innovative Medicine
// franchise naming — confirm with business before treating as final.
const TA_LABELS = {
  'ID Vaccine':                        'Infectious Disease',
  'CAPLYTA MSLs':                      'Neuroscience',
  'SCZ':                               'Neuroscience',
  'Mood':                              'Neuroscience',
  'Autoantibody-Neuroimmunology':      'Immunology',
  'Autoantibody - Pipeline':           'Immunology',
  'Gastroenterology':                  'Immunology',
  'Rheumatology':                      'Immunology',
  'Dermatology':                       'Immunology',
  'Oncology Head & Neck Cancer MSLs':  'Oncology',
  'ONC - Hematology':                  'Oncology',
  'GU':                                'Oncology',
  'Lung':                              'Oncology',
  'Real World Value & Evidence Field': 'VESE',
};
const taLabel = code => TA_LABELS[code] || code || 'Unknown';

// ── Dashboard Page ─────────────────────────────────────────────
export default function DashboardPage({ onOpenFcr, onDigestNavigate }) {
  const { accounts } = useMsal();
  const firstName = (accounts[0]?.name || '').split(' ')[0] || null;
  const [aiDigestOpen, setAiDigestOpen] = useState(false);
  const [activeView, setActiveView]     = useState(0);
  const [regionToggle, setRegionToggle] = useState('ta');
  const [selectedTA, setSelectedTA]     = useState(null); // drill-down level 2: TA bucket name, or null for top-level
  const [selectedDisease, setSelectedDisease] = useState(null); // drill-down level 3: disease area (fran_nm), or null
  const [fdRegions, setFdRegions]       = useState([]);   // level-3 bar data: [{ region, count, fd_name, fd_wwid, vacant_count }]
  const [fdLoading, setFdLoading]       = useState(false);
  const [selectedFD, setSelectedFD]     = useState(null); // drill-down level 4: { fd_wwid, fd_name, region }, or null
  const [fdReps, setFdReps]             = useState([]);   // level-4 MSL list: [{ name, wwid, territory, job_title, is_vacant, fcr_count }]
  const [fdRepsLoading, setFdRepsLoading] = useState(false);
  const [selectedMslRep, setSelectedMslRep] = useState(null); // MSL clicked in the level-4 list -> opens their FCR list
  const [summary, setSummary]               = useState(null);
  const [summaryLoading, setSummaryLoading]   = useState(true);
  const [summaryRefreshing, setSummaryRefreshing] = useState(false);
  // Field head (org lead) per disease area — pulled live from org.hierarchy
  // via /api/field-heads instead of a hardcoded object, so it can't silently
  // go stale/incomplete (see server.js buildFieldHeadsPayload).
  const [fieldHeads, setFieldHeads] = useState({});
  // Region dropdown options — starts with the static fallback list so the
  // dropdown isn't empty on first paint, then replaced with the real
  // distinct region values from /api/regions once it loads (see below).
  const [regionOptions, setRegionOptions] = useState(REGION_OPTIONS);

  const trackFilterChange = (filterType, value) => {
    const eventValue = value ?? 'all';
    telemetry.trackCustomEvent('filter_applied', {
      eventName: SUMMARY_FILTER_EVENT_NAMES[filterType]?.[eventValue] || 'filter_applied',
      page: 'dashboard',
      filterType,
      value: eventValue,
    });
  };

  // Filters
  const [filterTA,        setFilterTA]        = useState(null);
  const [filterTimeframe, setFilterTimeframe] = useState(null);
  const [filterRegion,    setFilterRegion]    = useState(null);
  const [customFrom,      setCustomFrom]      = useState('');
  const [customTo,        setCustomTo]        = useState('');
  const [openDropdown,    setOpenDropdown]    = useState(null);
  const filterBarRef = useRef(null);

  // ── "More filters" (2026-09-04): Therapy/Organization/Geography/FCR ──
  const [showMoreFilters,     setShowMoreFilters]     = useState(false);
  const [filterDiseaseArea,   setFilterDiseaseArea]   = useState(null);
  const [filterFieldHead,     setFilterFieldHead]     = useState(null);
  const [filterFieldDirector, setFilterFieldDirector] = useState(null);
  const [filterMsl,           setFilterMsl]           = useState(null);
  const [filterJobRole,       setFilterJobRole]       = useState(null);
  const [filterTerritory,     setFilterTerritory]     = useState(null);
  const [filterTrainingNeeded, setFilterTrainingNeeded] = useState(null);

  // ── RBAC "View As" scope (testing — see Topbar's picker + src/utils/viewAs.js) ──
  // When a Field Head persona is active, jump straight to the Field-Director
  // drill-down level for their locked disease area (skipping the top-level
  // TA-bucket / disease-area selection steps a real Field Head would never
  // need) and lock the Disease Area filter so it can't be widened from the
  // UI. The backend's X-View-As middleware is what actually enforces the
  // data scoping (see server.js) — this just makes the UI match it.
  const [viewAsScope, setViewAsScopeLocal] = useState(getViewAsScope());
  useEffect(() => {
    const sync = () => setViewAsScopeLocal(getViewAsScope());
    window.addEventListener('viewAsChanged', sync);
    return () => window.removeEventListener('viewAsChanged', sync);
  }, []);
  const isFieldHeadView = viewAsScope?.role === 'field_head' && !!viewAsScope.diseaseArea;
  // A Field Head can own MULTIPLE disease areas (a real org pattern — e.g.
  // one person heading both "Autoantibody - Pipeline" AND
  // "Autoantibody-Neuroimmunology"; confirmed 2026-09-24: 4 real Field
  // Heads span 2-3 areas each). `viewAsScope.diseaseAreas` (plural, from
  // /api/rbac/personas grouping by wwid) is the authoritative list;
  // `.diseaseArea` (singular) stays a back-compat alias (= areas[0]).
  const fieldHeadDiseaseAreas = isFieldHeadView
    ? (viewAsScope.diseaseAreas?.length ? viewAsScope.diseaseAreas : [viewAsScope.diseaseArea])
    : [];
  const hasSingleFieldHeadDiseaseArea = isFieldHeadView && fieldHeadDiseaseAreas.length === 1;
  // Which TA bucket(s) a multi-disease Field Head's own areas fall into —
  // almost always exactly 1 in practice (confirmed 2026-09-24: all 4 real
  // multi-disease Field Heads today have every one of their areas share a
  // single bucket), which is what lets the effect below skip the redundant
  // single-bar TA level. Computed once here and reused by both that effect
  // and isFieldHeadHomeLevel so they can never drift out of sync on what
  // counts as her "top" level.
  const fieldHeadTaBuckets = isFieldHeadView ? [...new Set(fieldHeadDiseaseAreas.map(taLabel))] : [];
  const hasSingleFieldHeadTaBucket = fieldHeadTaBuckets.length === 1;
  useEffect(() => {
    if (hasSingleFieldHeadDiseaseArea) {
      setRegionToggle('ta');
      setSelectedTA(viewAsScope.therapeuticArea || viewAsScope.diseaseArea);
      setSelectedDisease(viewAsScope.diseaseArea);
      setFilterDiseaseArea(viewAsScope.diseaseArea);
      // IMPORTANT: do NOT also set filterTA/filterFieldHead here. Every
      // active filter (ta, diseaseArea, fieldHead, ...) gets combined into
      // ONE query object for /api/summary and /api/fcrs (see
      // buildActiveFilterParams below), and that combined object is the
      // cache key. The nightly warm-up only pre-computes SINGLE-dimension
      // variants ({diseaseArea:X} alone, {ta:X} alone, etc.) — never
      // combos. Auto-setting ta+fieldHead ALONGSIDE diseaseArea silently
      // turned every Field Head's dashboard load into a 3-dimension combo
      // that was NEVER cached, forcing a live ~10s Redshift query on every
      // single view (bug found 2026-09-18: only the 2-3 Field Heads someone
      // had coincidentally already loaded that exact combo for looked fast).
      // `diseaseArea` alone is already a complete, sufficient lock (each
      // disease area belongs to exactly one TA and one Field Head) — see
      // `effectiveFieldHeadWwid` below for how the org-side dropdown
      // cascades (Field Director/MSL/Job Role) get their own scope instead.
    } else if (isFieldHeadView && fieldHeadDiseaseAreas.length > 1) {
      // Multi-disease Field Head: if ALL her areas happen to bucket into
      // the SAME Therapeutic Area (the common case — e.g. Kathryn
      // Bercury-Russell's Pipeline + Neuroimmunology are both
      // "Immunology"), auto-select that ONE bucket so she lands directly
      // on the disease-breakdown chart (her own N areas as bars, which she
      // clicks to drill into that disease's Field Directors) instead of a
      // redundant "click to reveal your only 1 TA bucket" step first.
      // Never auto-selects a specific DISEASE (selectedDisease stays null)
      // — which of her own areas to drill into is a real choice for her.
      // If her areas span MULTIPLE TA buckets (rare), leave selectedTA
      // null too — there's genuine ambiguity, so she sees the normal
      // top-level TA-bucket chart (still restricted to just her own
      // buckets server-side) and picks one first.
      if (hasSingleFieldHeadTaBucket) {
        setRegionToggle('ta');
        setSelectedTA(fieldHeadTaBuckets[0]);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasSingleFieldHeadDiseaseArea, isFieldHeadView, viewAsScope?.diseaseArea, viewAsScope?.diseaseAreas?.join(',')]);

  // Field Director "View As" scope: one level narrower than a Field Head —
  // locked not just to their disease area but to their OWN team within it
  // (see the X-View-As middleware's `query.fieldDirector = scope.wwid` lock
  // in server.js, enforced on every data endpoint via resolveOrgFilters()).
  // Jump straight to drill-down level 4 (the MSL team list — no bar chart,
  // see isDrilledIntoMsls below) instead of the Field-Director bar chart a
  // Field Head sees: a Field Director only has the one team, so there's
  // nothing to drill INTO first.
  const isFieldDirectorView = viewAsScope?.role === 'field_director' && !!viewAsScope.diseaseArea && !!viewAsScope.wwid;
  useEffect(() => {
    if (isFieldDirectorView) {
      setRegionToggle('ta');
      setSelectedTA(viewAsScope.therapeuticArea || viewAsScope.diseaseArea);
      setSelectedDisease(viewAsScope.diseaseArea);
      setFilterDiseaseArea(viewAsScope.diseaseArea);
      setFilterFieldDirector(viewAsScope.wwid);
      setSelectedFD({ fd_wwid: viewAsScope.wwid, fd_name: viewAsScope.fdName, region: viewAsScope.region });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isFieldDirectorView, viewAsScope?.wwid]);

  // The wwid used to scope the Field Director/MSL/Job Role dropdown
  // cascades (org.hierarchy-side, NOT part of the Redshift diseaseArea
  // query above): a locked Field Head's own wwid, or whatever an Enterprise
  // user manually picked from the Field Head dropdown. Kept separate from
  // `filterFieldHead` state itself so a locked Field Head's identity never
  // leaks into the /api/summary or /api/fcrs cache key (see the comment
  // above for why that broke caching).
  const effectiveFieldHeadWwid = isFieldHeadView ? viewAsScope.wwid : filterFieldHead;

  // AI Digest scope — mirrors the same active filters /api/summary already
  // uses (buildActiveFilterParams below), so the digest's numbers always
  // match what's currently on screen. The backend's X-View-As middleware
  // re-locks diseaseArea/region server-side regardless of what's sent here
  // for a locked Field Head/Field Director persona — this is just what the
  // page's OWN filter bar currently has selected.
  const aiDigestScope = {
    firstName,
    ta: filterTA,
    region: filterRegion,
    diseaseArea: isFieldHeadView ? viewAsScope.diseaseArea : filterDiseaseArea,
    territory: filterTerritory,
    trainingNeeded: filterTrainingNeeded,
    timeframe: filterTimeframe && filterTimeframe !== 'custom' ? filterTimeframe : null,
  };

  const [diseaseAreaOptions, setDiseaseAreaOptions] = useState([{ label: 'All disease areas', value: null }]);
  const [fieldHeadOptions,     setFieldHeadOptions]     = useState([{ label: 'All field heads', value: null }]);
  const [fieldDirectorOptions, setFieldDirectorOptions] = useState([{ label: 'All field directors', value: null }]);
  const [mslOptions,           setMslOptions]           = useState([{ label: 'All MSLs', value: null }]);
  const [jobRoleOptions,       setJobRoleOptions]       = useState([{ label: 'All job roles', value: null }]);
  const [territoryOptions,     setTerritoryOptions]     = useState([{ label: 'All territories', value: null }]);
  const TRAINING_NEEDED_OPTIONS = [
    { label: 'Any',   value: null },
    { label: 'Yes',   value: 'yes' },
    { label: 'No',    value: 'no' },
  ];

  // Static lists, fetched once (field heads never depend on another filter).
  useEffect(() => {
    fetch('/api/filters/field-heads')
      .then(r => r.json())
      .then(d => setFieldHeadOptions([{ label: 'All field heads', value: null }, ...(d.fieldHeads || []).map(f => ({ label: f.name, value: f.wwid }))]))
      .catch(() => {});
  }, []);

  // Disease Area cascades from the selected Therapeutic Area (or full list
  // if none) — mirrors the Territory-cascades-from-Disease-Area effect below.
  useEffect(() => {
    const p = filterTA ? `?ta=${encodeURIComponent(filterTA)}` : '';
    fetch(`/api/filters/disease-areas${p}`)
      .then(r => r.json())
      .then(d => setDiseaseAreaOptions([{ label: 'All disease areas', value: null }, ...(d.diseaseAreas || [])]))
      .catch(() => {});
  }, [filterTA]);

  // Clear a selected Disease Area that no longer belongs to the newly
  // selected Therapeutic Area (same reasoning as other filter cascades).
  useEffect(() => {
    if (!filterTA || !filterDiseaseArea) return;
    if (!(TA_GROUP_TO_FRANS[filterTA] || []).includes(filterDiseaseArea)) {
      setFilterDiseaseArea(null);
    }
  }, [filterTA]);

  // Job Role cascades from the selected/locked Field Head (or full list if
  // none). Mirrors the Field Director cascade below — same reasoning: a
  // locked Field Head should only ever see job titles that exist within
  // their own org, not every title company-wide.
  useEffect(() => {
    const p = effectiveFieldHeadWwid ? `?fieldHead=${encodeURIComponent(effectiveFieldHeadWwid)}` : '';
    fetch(`/api/filters/job-roles${p}`)
      .then(r => r.json())
      .then(d => setJobRoleOptions([{ label: 'All job roles', value: null }, ...(d.jobRoles || []).map(r => ({ label: r, value: r }))]))
      .catch(() => {});
  }, [effectiveFieldHeadWwid]);

  // Territory cascades from the selected/locked Disease Area (or full list
  // if none) — territories live in Redshift (fran_nm), not org.hierarchy.
  useEffect(() => {
    const p = filterDiseaseArea ? `?diseaseArea=${encodeURIComponent(filterDiseaseArea)}` : '';
    fetch(`/api/filters/territories${p}`)
      .then(r => r.json())
      .then(d => setTerritoryOptions([{ label: 'All territories', value: null }, ...(d.territories || []).map(t => ({ label: t.territory, value: t.territory }))]))
      .catch(() => {});
  }, [filterDiseaseArea]);

  // Field Directors cascade from the selected/locked Field Head (or full list if none selected).
  useEffect(() => {
    const p = effectiveFieldHeadWwid ? `?fieldHead=${encodeURIComponent(effectiveFieldHeadWwid)}` : '';
    fetch(`/api/filters/field-directors${p}`)
      .then(r => r.json())
      .then(d => setFieldDirectorOptions([{ label: 'All field directors', value: null }, ...(d.fieldDirectors || []).map(f => ({ label: f.name, value: f.wwid }))]))
      .catch(() => {});
  }, [effectiveFieldHeadWwid]);

  // MSLs (optional dimension) cascade from the selected Field Director, or
  // (RBAC) fall back to the locked/selected Field Head's whole org when no
  // specific Field Director has been chosen yet — mirrors the backend's own
  // `/api/filters/msls` fallback (fieldDirector takes priority, fieldHead is
  // the fallback). Without this fallback, a Field Head saw EVERY MSL
  // company-wide until they also picked one specific Field Director first.
  useEffect(() => {
    const params = new URLSearchParams();
    if (filterFieldDirector) params.set('fieldDirector', filterFieldDirector);
    else if (effectiveFieldHeadWwid) params.set('fieldHead', effectiveFieldHeadWwid);
    const qs = params.toString();
    fetch(`/api/filters/msls${qs ? `?${qs}` : ''}`)
      .then(r => r.json())
      .then(d => setMslOptions([{ label: 'All MSLs', value: null }, ...(d.msls || []).map(m => ({ label: m.name, value: m.wwid }))]))
      .catch(() => {});
  }, [filterFieldDirector, effectiveFieldHeadWwid]);

  const moreFiltersActiveCount = [
    filterDiseaseArea, filterFieldHead, filterFieldDirector, filterMsl,
    filterJobRole, filterTerritory, filterTrainingNeeded,
  ].filter(Boolean).length;

  // Panel state for the "More filters" FCR list drill-in (Bug 1: MSL, Bug 2: Region).
  const [fcrListPanel, setFcrListPanel] = useState(null); // { title, subtitle, queryParams } | null

  // Builds the exact query-string params for the CURRENT filter selection —
  // shared by the /api/summary fetch (KPI numbers) AND the FCR list panel
  // (Bug 1/2 fix), so the count shown always matches the list contents.
  const buildActiveFilterParams = () => {
    const p = new URLSearchParams();
    if (filterTA) p.set('ta', filterTA);
    if (filterRegion) p.set('region', filterRegion);
    if (filterTimeframe && filterTimeframe !== 'custom') p.set('timeframe', filterTimeframe);
    if (filterTimeframe === 'custom' && customFrom) p.set('from', customFrom);
    if (filterTimeframe === 'custom' && customTo)   p.set('to',   customTo);
    if (filterDiseaseArea)    p.set('diseaseArea', filterDiseaseArea);
    if (filterFieldHead)      p.set('fieldHead', filterFieldHead);
    if (filterFieldDirector)  p.set('fieldDirector', filterFieldDirector);
    if (filterMsl)            p.set('msl', filterMsl);
    if (filterJobRole)        p.set('jobRole', filterJobRole);
    if (filterTerritory)      p.set('territory', filterTerritory);
    if (filterTrainingNeeded) p.set('trainingNeeded', filterTrainingNeeded);
    return p;
  };

  // Close dropdowns when clicking outside the filter bar
  useEffect(() => {
    const handler = e => {
      if (filterBarRef.current && !filterBarRef.current.contains(e.target)) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Fetch field heads once on mount (cached server-side, all disease areas
  // at once — doesn't depend on filters).
  useEffect(() => {
    fetch('/api/field-heads')
      .then(r => r.json())
      .then(d => setFieldHeads(d && !d.error ? d : {}))
      .catch(() => setFieldHeads({}));
  }, []);

  // Populate the Region filter dropdown dynamically from the actual distinct
  // region values in the data (bucketed server-side via REGION_CLEAN_EXPR —
  // see /api/regions), instead of the static 5-option fallback above.
  useEffect(() => {
    fetch('/api/regions')
      .then(r => r.json())
      .then(d => {
        const rows = d?.regions || [];
        if (!rows.length) return;
        setRegionOptions([
          { label: 'All regions', value: null },
          ...rows.map(r => ({ label: r.region, value: r.region })),
        ]);
      })
      .catch(() => {});
  }, []);

  // Fetch summary with stale-while-revalidate
  useEffect(() => {
    const p = buildActiveFilterParams();
    // BUG FIX 2026-09-24: this cache key used to be built from `p` ALONE —
    // for a locked Field Head/Field Director whose own scope narrows things
    // the UI's own filter bar never sets (diseaseArea for a multi-disease
    // Field Head is enforced entirely server-side, see isFieldHeadView's
    // effect above), `p` can be IDENTICAL (often empty) across two
    // completely different people/personas. Switching "View As" personas
    // would then flash the PREVIOUS persona's stale localStorage entry
    // under the same key before the live fetch corrects it. Folding the
    // scope's own identity (role + wwid + diseaseAreas) into the key means
    // two different locked identities can never collide on one cache entry.
    const scopeFingerprint = viewAsScope
      ? `${viewAsScope.role}:${viewAsScope.wwid || ''}:${(viewAsScope.diseaseAreas || (viewAsScope.diseaseArea ? [viewAsScope.diseaseArea] : [])).join(',')}`
      : 'enterprise';
    const cacheKey = `fcr_summary_${scopeFingerprint}_${p.toString()}`;
    // Show stale data immediately if available
    try {
      const stale = localStorage.getItem(cacheKey);
      if (stale) { setSummary(JSON.parse(stale)); setSummaryLoading(false); setSummaryRefreshing(true); }
      else { setSummaryLoading(true); }
    } catch { setSummaryLoading(true); }
    fetch(`/api/summary?${p}`)
      .then(r => r.json())
      .then(d => {
        setSummary(d); setSummaryLoading(false); setSummaryRefreshing(false);
        try { localStorage.setItem(cacheKey, JSON.stringify(d)); } catch {}
      })
      .catch(() => { setSummaryLoading(false); setSummaryRefreshing(false); });
  }, [filterTA, filterTimeframe, filterRegion, customFrom, customTo,
      filterDiseaseArea, filterFieldHead, filterFieldDirector, filterMsl, filterJobRole, filterTerritory, filterTrainingNeeded,
      viewAsScope?.role, viewAsScope?.wwid, viewAsScope?.diseaseArea]);

  // Derive display values
  const kpi = summary?.kpi;
  const fcrsByRegion = summary?.by_region?.map(r => ({ region: r.region.replace(/ - .*/, '').trim(), count: Number(r.fcrs) })) || fcrByRegion;

  // Disease area (fran_nm) -> real per-region FCR counts, from Redshift's
  // reg_nm field (the app's standard Northeast/Southeast/Central/West/East
  // buckets — not the custom region names used in the director directory).
  const diseaseRegionMap = (() => {
    const map = new Map();
    for (const r of summary?.by_ta_region || []) {
      const disease = r.ta || 'Unknown';
      if (!map.has(disease)) map.set(disease, []);
      map.get(disease).push({ region: r.region, count: Number(r.fcrs) });
    }
    for (const list of map.values()) list.sort((a, b) => b.count - a.count);
    return map;
  })();

  // Long franchise names get a short display label on the drill-down chart
  // axis (full name still shown in the tooltip via `fullName`).
  const SHORT_FRAN = {
    'Autoantibody - Pipeline':      'Pipeline',
    'Autoantibody-Neuroimmunology': 'Neuroimmunology',
    'ONC - Hematology':             'Hematology',
    'Oncology Head & Neck Cancer MSLs': 'Head & Neck Cancer',
  };

  // Bucket raw franchise (fran_nm) rows into TA groups, and keep the
  // underlying sub-groups per bucket for drill-down.
  const { fcrsByTA, taSubGroups } = (() => {
    if (!summary?.by_ta) return { fcrsByTA: [], taSubGroups: new Map() };
    const buckets = new Map();      // TA label -> total count
    const subGroups = new Map();    // TA label -> [{ region: fran_nm, count }]
    for (const r of summary.by_ta) {
      const label = taLabel(r.ta);
      const count = Number(r.fcrs);
      buckets.set(label, (buckets.get(label) || 0) + count);
      if (!subGroups.has(label)) subGroups.set(label, []);
      const raw = r.ta || 'Unknown';
      subGroups.get(label).push({ region: SHORT_FRAN[raw] || raw, fullName: raw, count, fieldHead: fieldHeads[raw] });
    }
    for (const list of subGroups.values()) list.sort((a, b) => b.count - a.count);
    const fcrsByTA = [...buckets.entries()]
      .map(([region, count]) => ({ region, count }))
      .sort((a, b) => b.count - a.count);
    return { fcrsByTA, taSubGroups: subGroups };
  })();

  const isDrilledDown = regionToggle === 'ta' && selectedTA;
  const isDrilledIntoFDs = isDrilledDown && selectedDisease;
  const isDrilledIntoMsls = isDrilledIntoFDs && selectedFD;
  const barChartData = isDrilledIntoFDs
    ? fdRegions
    : isDrilledDown
      ? (taSubGroups.get(selectedTA) || [])
      : (regionToggle === 'ta' ? fcrsByTA : fcrsByRegion);
  // Dynamic Y-axis for the bar chart — zooms to the current drill-down
  // level's own data range instead of a one-size-fits-all scale.
  const barChartAxis = getCountAxis(barChartData.map(d => d.count));
  const barChartLabel = isDrilledIntoMsls
    ? `MSL team — ${selectedFD.region} · Field Director: ${selectedFD.fd_name}`
    : isDrilledIntoFDs
      ? `Field Directors — ${SHORT_FRAN[selectedDisease] || selectedDisease}`
      : isDrilledDown
        ? `Disease areas in ${selectedTA}`
        : (regionToggle === 'ta' ? 'FCRs by therapeutic area' : 'FCRs by region');

  // Level 3: fetch real Field Director + region data (org.hierarchy +
  // Redshift FCR counts) whenever a disease-area bar is clicked.
  useEffect(() => {
    if (!selectedDisease) { setFdRegions([]); return; }
    let cancelled = false;
    setFdLoading(true);
    fetch(`/api/field-directors?ta=${encodeURIComponent(selectedDisease)}`)
      .then(r => r.json())
      .then(d => {
        if (cancelled) return;
        const rows = (d.field_directors || []).map(fd => ({
          region: fd.region || fd.fd_name,
          count: Number(fd.total_fcrs) || 0,
          fd_name: fd.fd_name,
          fd_wwid: fd.fd_wwid,
          vacant_count: fd.vacant_count,
        }));
        setFdRegions(rows);
        setFdLoading(false);
      })
      .catch(() => { if (!cancelled) setFdLoading(false); });
    return () => { cancelled = true; };
  }, [selectedDisease]);

  // Level 4: fetch the MSL team + real FCR counts for the clicked Field
  // Director (org.hierarchy for the roster, Redshift for each rep's FCRs).
  useEffect(() => {
    if (!selectedFD) { setFdReps([]); return; }
    let cancelled = false;
    setFdRepsLoading(true);
    fetch(`/api/field-director/${encodeURIComponent(selectedFD.fd_wwid)}/reps`)
      .then(r => r.json())
      .then(d => {
        if (cancelled) return;
        setFdReps(d.reps || []);
        setFdRepsLoading(false);
      })
      .catch(() => { if (!cancelled) setFdRepsLoading(false); });
    return () => { cancelled = true; };
  }, [selectedFD]);

  const handleBarClick = (data) => {
    if (regionToggle === 'ta' && !selectedTA && data?.region) {
      telemetry.trackCustomEvent('chart_drilldown', { page: 'dashboard', chart: 'fcr-coverage', level: 'therapeutic-area' });
      setSelectedTA(data.region);
    } else if (regionToggle === 'ta' && selectedTA && !selectedDisease && data?.fullName) {
      telemetry.trackCustomEvent('chart_drilldown', { page: 'dashboard', chart: 'fcr-coverage', level: 'disease-area' });
      setSelectedDisease(data.fullName);
    } else if (isDrilledIntoFDs && !selectedFD && data?.fd_wwid) {
      telemetry.trackCustomEvent('chart_drilldown', { page: 'dashboard', chart: 'fcr-coverage', level: 'field-director' });
      setSelectedFD({ fd_wwid: data.fd_wwid, fd_name: data.fd_name, region: data.region });
    }
  };

  // Step back one drill-down level at a time: MSLs -> FDs -> diseases -> top-level.
  // A locked Field Head "View As" scope with a SINGLE disease area can
  // never step back past that disease level (level 3) — that's the top of
  // their world. A Field Head locked to MULTIPLE disease areas (see
  // fieldHeadDiseaseAreas above) CAN step back out of one disease to pick
  // another — the backend still only ever returns data for their own
  // areas regardless of how far back they navigate, so there's nothing
  // wider to protect against — but can never clear the auto-selected
  // shared TA bucket itself (see isFieldHeadHomeLevel below): that's THEIR
  // top level, same role a single disease area plays for the simpler case.
  // A locked Field Director can never step back at ALL — their MSL team IS
  // the top of their world (there's no Back button rendered for them
  // either, see below, but this guards against the handler firing some
  // other way too).
  const handleBack = () => {
    if (selectedFD && !isFieldDirectorView) setSelectedFD(null);
    else if (selectedDisease && !hasSingleFieldHeadDiseaseArea && !isFieldDirectorView) setSelectedDisease(null);
    // The rare multi-TA-bucket case (see isFieldHeadHomeLevel below) needs
    // its OWN selectedTA cleared too, to get back to the bucket picker —
    // guarding on `!isFieldHeadHomeLevel` (not `!isFieldHeadView`) lets that
    // happen for a Field Head while still refusing to clear a single-bucket
    // Field Head's or single-disease Field Head's already-home selectedTA.
    else if (!isFieldHeadHomeLevel && !isFieldDirectorView) setSelectedTA(null);
  };
  // The drill-down level that counts as a Field Head's OWN top level (no
  // Back button rendered, handleBack above is a no-op there): for a
  // single-disease Field Head that's always level 3 (their one disease's
  // Field-Directors chart, selectedFD not yet picked). For a multi-disease
  // Field Head whose areas share one TA bucket (auto-selected — see the
  // effect above) it's the disease-breakdown chart itself (selectedDisease
  // not yet picked). For the rare multi-BUCKET case (selectedTA never
  // auto-set), it's the very top (selectedTA not yet picked) — otherwise
  // she'd have no Back button to return to her OTHER bucket's diseases.
  const isFieldHeadHomeLevel = isFieldHeadView && (
    hasSingleFieldHeadDiseaseArea ? !selectedFD
    : hasSingleFieldHeadTaBucket ? !selectedDisease
    : !selectedTA
  );
  // Required Base = distinct MSLs on the Field Coaching Report roster that
  // quarter (coached or not) — the real denominator for "1 FCR per MSL per
  // quarter". `coached` = distinct MSLs who got >=1 completed FCR; `repeats`
  // = extra FCRs beyond one per coached MSL; `coverage` = coached/required.
  const fcrsTrend = summary?.trend?.map(r => {
    const coached = Number(r.coached);
    const required_fcrs = Number(r.required_fcrs);
    return {
      quarter: r.quarter,
      total_fcrs: Number(r.total_fcrs),
      coached,
      repeats: Number(r.repeats),
      required_fcrs,
      coverage: required_fcrs > 0 ? Math.round((coached / required_fcrs) * 100) : 0,
    };
  }) || completionTrend;
  const latestQuarter = fcrsTrend.length ? fcrsTrend[fcrsTrend.length - 1] : null;
  const prevQuarter    = fcrsTrend.length > 1 ? fcrsTrend[fcrsTrend.length - 2] : null;
  // Dynamic Y-axis for the coverage chart — zooms to the actual stacked bar
  // heights (coached + repeats) and the required-base line, instead of a
  // fixed ceiling that leaves the bars looking artificially small.
  const coverageAxis = getCountAxis(
    fcrsTrend.flatMap(r => [r.coached + r.repeats, r.required_fcrs])
  );
  // Single reference-line value for the whole chart — the current/latest
  // quarter's Required Base (each bar's own coverage % still uses that
  // quarter's own required_fcrs, computed above).
  const requiredFcrs   = latestQuarter?.required_fcrs || 0;
  const paceGap        = latestQuarter ? latestQuarter.coached - latestQuarter.required_fcrs : 0;
  const isAheadOfPace  = paceGap >= 0;
  const isTrendingUp   = prevQuarter && latestQuarter ? latestQuarter.coached >= prevQuarter.coached : true;
  const fmt = n => n != null ? Number(n).toLocaleString() : '—';

  // MSL vs VESE split (within the combined "MSL/VESE Field Coaching Report")
  const mslCount  = Number(summary?.by_report_type?.find(r => r.report_type === 'MSL')?.fcrs)  || 0;
  const veseCount = Number(summary?.by_report_type?.find(r => r.report_type === 'VESE')?.fcrs) || 0;

  const timeframeLabel = filterTimeframe === null ? 'All time'
    : filterTimeframe === '7'      ? 'Past 7 days'
    : filterTimeframe === '30'     ? 'Past 30 days'
    : filterTimeframe === '90'     ? 'Past quarter'
    : filterTimeframe === '180'    ? 'Past 6 months'
    : filterTimeframe === '365'    ? 'Past year'
    : filterTimeframe === 'custom' ? (customFrom || customTo ? `${customFrom || '…'} → ${customTo || '…'}` : 'Custom range')
    : 'All time';

  const activeFilterCount = [filterTA, filterTimeframe, filterRegion].filter(Boolean).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

      {/* ── HERO SUMMARY CARD ── */}
      <div className="dash-card">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: '#D71600', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <Layers size={20} color="#fff" />
            </div>
            <div>
              <div className="section-eyebrow">Summary · {timeframeLabel}{filterTA ? ` · ${filterTA}` : ''}{filterRegion ? ` · ${filterRegion}` : ''}</div>
              <div style={{ fontSize: 22, fontWeight: 800, color: '#1A1A1A', marginTop: 2, letterSpacing: '-0.3px' }}>
                Coaching activity at a glance
              </div>
            </div>
          </div>
          {summaryRefreshing ? (
            <div className="refresh-pill">
              <span className="refresh-spin" />
              Refreshing data…
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 6 }}>
              <div className="sync-pill"><CheckCircle2 size={12} color="#16A34A" /> MSL/VESE FCRs · Synced from iConnect · Live</div>
              {!summaryLoading && (
                <div style={{ fontSize: 11, color: '#6B7280', display: 'flex', gap: 8 }}>
                  <span><strong style={{ color: '#1A1A1A' }}>{fmt(mslCount)}</strong> MSL</span>
                  <span style={{ color: '#D1D5DB' }}>|</span>
                  <span><strong style={{ color: '#1A1A1A' }}>{fmt(veseCount)}</strong> VESE</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* KPI tiles */}
        <div className="kpi-grid">
          <KpiTile label="MSL FCRs Written"       tag={timeframeLabel}
            value={summaryLoading ? <><span className="skeleton skeleton-value" /><span className="skeleton skeleton-sub" /></> : fmt(kpi?.total_fcrs)}
            sub={summaryLoading ? null : `${mslCount} MSL · ${veseCount} VESE`}
            accent="red" />
          <KpiTile label="MSLs Coached"           tag={timeframeLabel}
            value={summaryLoading ? <><span className="skeleton skeleton-value" /><span className="skeleton skeleton-sub" /></> : fmt(kpi?.total_reps)}
            sub={summaryLoading ? null : `${kpi?.fcrs_per_rep ?? '—'} FCRs written per MSL`}
            accent="green" />
          <KpiTile label="FCRs Flagging Training" tag={timeframeLabel}
            value={summaryLoading ? <><span className="skeleton skeleton-value" /><span className="skeleton skeleton-sub" /></> : fmt(kpi?.fcrs_flagging_training)}
            sub={summaryLoading ? null : `${kpi?.training_fcrs_pct ?? 0}% of all FCRs`}
            accent="amber" />
          <KpiTile label="MSLs Needing Training"  tag={timeframeLabel}
            value={summaryLoading ? <><span className="skeleton skeleton-value" /><span className="skeleton skeleton-sub" /></> : fmt(kpi?.msls_needing_training)}
            sub={summaryLoading ? null : `${kpi?.training_reps_pct ?? 0}% of the team`}
            accent="redhl" highlighted />
        </div>
      </div>

      {/* ── FILTER ROW ── */}
      {/* NOTE: flexWrap must be overridden to 'nowrap' here — the shared
          .filter-row class sets flex-wrap:wrap for its normal single-row
          usage (CapabilityPage/FCRsPage), but combined with flex-direction:
          column (this page's expandable "More filters" layout) it triggers
          a flexbox multi-line sizing quirk that inflates the container to
          a huge phantom height with a big empty gap below the content. */}
      <div className="filter-row" ref={filterBarRef} style={{ flexDirection: 'column', alignItems: 'stretch', flexWrap: 'nowrap', gap: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: '#1A1A1A', display: 'flex', alignItems: 'center', gap: 4 }}>
              <Filter size={13} /> Filters {(activeFilterCount + moreFiltersActiveCount) > 0 && <span style={{ background: '#D71600', color: '#fff', borderRadius: 20, fontSize: 10, padding: '1px 6px', fontWeight: 700 }}>{activeFilterCount + moreFiltersActiveCount}</span>}
            </span>

            {/* Timeframe */}
            <FilterDropdown
              id="timeframe" label="Timeframe" icon={Calendar}
              options={TIMEFRAME_OPTIONS}
              value={filterTimeframe}
              onChange={value => { trackFilterChange('timeframe', value); setFilterTimeframe(value); }}
              open={openDropdown === 'timeframe'}
              onToggle={setOpenDropdown}
              extra={filterTimeframe === 'custom' && (
                <div style={{ padding: '10px 14px', borderTop: '1px solid #F3F4F6', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: '#6B7280', marginBottom: 2 }}>Custom date range</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div>
                      <div style={{ fontSize: 11, color: '#6B7280', marginBottom: 3 }}>From</div>
                      <input type="date" value={customFrom} onChange={e => {
                        telemetry.trackCustomEvent('summary_filter_custom_from_set', { page: 'summary', filter: 'timeframe_custom_from', hasValue: Boolean(e.target.value) });
                        setCustomFrom(e.target.value);
                      }}
                        style={{ fontSize: 12, border: '1px solid #E9E5E7', borderRadius: 7, padding: '5px 8px', width: '100%', outline: 'none', color: '#1B1F2A' }} />
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: '#6B7280', marginBottom: 3 }}>To</div>
                      <input type="date" value={customTo} onChange={e => {
                        telemetry.trackCustomEvent('summary_filter_custom_to_set', { page: 'summary', filter: 'timeframe_custom_to', hasValue: Boolean(e.target.value) });
                        setCustomTo(e.target.value);
                      }}
                        style={{ fontSize: 12, border: '1px solid #E9E5E7', borderRadius: 7, padding: '5px 8px', width: '100%', outline: 'none', color: '#1B1F2A' }} />
                    </div>
                  </div>
                  <button onMouseDown={() => {
                    telemetry.trackCustomEvent('custom_date_applied', { eventName: 'summary_filter_custom_date_applied', page: 'dashboard', hasFrom: Boolean(customFrom), hasTo: Boolean(customTo) });
                    setOpenDropdown(null);
                  }}
                    style={{ background: '#D71600', color: '#fff', border: 'none', borderRadius: 8, padding: '6px 0', fontSize: 12, fontWeight: 700, cursor: 'pointer', marginTop: 2 }}>
                    Apply
                  </button>
                </div>
              )}
            />

            {/* Therapeutic Area + Region hidden once expanded — they move down into the Therapy/Geography groups below */}
            {!showMoreFilters && (
              <>
                <FilterDropdown
                  id="ta" label="Therapeutic Area" icon={Briefcase}
                  options={TA_OPTIONS}
                  value={filterTA}
                  onChange={value => { trackFilterChange('therapeutic-area', value); setFilterTA(value); }}
                  open={openDropdown === 'ta'}
                  onToggle={setOpenDropdown}
                  disabled={isFieldHeadView || isFieldDirectorView}
                />
                <FilterDropdown
                  id="region" label="Region" icon={MapPin}
                  options={regionOptions}
                  value={filterRegion}
                  onChange={value => { trackFilterChange('region', value); setFilterRegion(value); }}
                  open={openDropdown === 'region'}
                  onToggle={setOpenDropdown}
                  disabled={isFieldDirectorView}
                />
              </>
            )}

            {/* More / Less filters toggle */}
            <button
              className="filter-pill"
              onMouseDown={() => setShowMoreFilters(v => !v)}
              style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontWeight: 600 }}
            >
              <Grid3x3 size={14} />
              {showMoreFilters ? 'Less filters' : 'More filters'}
              <ChevronDown size={11} style={{ transform: showMoreFilters ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s' }} />
              {moreFiltersActiveCount > 0 && <span style={{ background: '#D71600', color: '#fff', borderRadius: 20, fontSize: 10, padding: '1px 6px', fontWeight: 700 }}>{moreFiltersActiveCount}</span>}
            </button>

            {/* Clear all */}
            {(activeFilterCount + moreFiltersActiveCount) > 0 && (
              <button
                className="filter-pill"
                onMouseDown={() => {
                  telemetry.trackButtonClick('dashboard-clear-filters', 'Clear all', { eventName: 'summary_filters_clear_all', page: 'dashboard' });
                  setFilterTimeframe(null); setCustomFrom(''); setCustomTo('');
                  setFilterMsl(null); setFilterTrainingNeeded(null);
                  // A locked Field Director "View As" scope owns Region /
                  // Field Director / Job Role / Territory themselves (see
                  // the disabled={isFieldDirectorView} locks above) — "Clear
                  // all" must never reset those back to null either, same
                  // reasoning as the Field Head guard below. MSL and
                  // Training Needed stay free filters for a Field Director,
                  // so they're cleared unconditionally above.
                  if (!isFieldDirectorView) {
                    setFilterRegion(null);
                    setFilterFieldDirector(null);
                    setFilterJobRole(null);
                    setFilterTerritory(null);
                  }
                  // A locked Field Head "View As" scope owns Therapeutic
                  // Area / Disease Area / Field Head themselves — "Clear
                  // all" must never reset those back to null, otherwise the
                  // UI would misleadingly show "All disease areas" while the
                  // backend (which always re-locks via the X-View-As header
                  // regardless of what the UI sends) keeps serving only
                  // their own scope. Only clear the OPTIONAL narrowing
                  // dimensions above for a locked Field Head.
                  if (!isFieldHeadView && !isFieldDirectorView) {
                    setFilterTA(null);
                    setFilterDiseaseArea(null);
                    setFilterFieldHead(null);
                  }
                }}
                style={{ color: '#D71600', borderColor: '#D71600', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 4 }}
              >
                <RotateCcw size={14} />
                Reset
              </button>
            )}
          </div>
          <span style={{ fontSize: 11, color: '#6B7280' }}>
            Showing <strong>{summaryLoading ? '…' : fmt(kpi?.total_fcrs)} FCRs</strong> · <strong>{summaryLoading ? '…' : fmt(kpi?.total_reps)} MSLs</strong>
            {showMoreFilters
              ? <> · <strong>{summaryLoading ? '…' : fmt(kpi?.total_field_directors)} Field Directors</strong></>
              : <> · <strong>{summaryLoading ? '…' : fmt(kpi?.submitted_fcrs)} Published</strong></>}
          </span>
        </div>

        {/* ── MORE FILTERS (expanded grouped panel) ──
            Mockup layout: each group's label sits INLINE to the left of its
            own pills (a horizontal row), with 2 groups per grid row (Therapy
            + Organization, then Geography + FCR) — not a label stacked above
            a vertical column of pills. */}
        {showMoreFilters && (
          <div className="more-filters-panel" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', alignItems: 'start', gap: '14px 28px', paddingTop: 8, borderTop: '1px solid #F3F4F6' }}>
            {/* Therapy */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', minWidth: 78, paddingTop: 6 }}>Therapy</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, flex: 1 }}>
                <FilterDropdown id="ta2" label="Therapeutic Area" icon={Briefcase} options={TA_OPTIONS} value={filterTA} onChange={value => { trackFilterChange('therapeutic-area', value); setFilterTA(value); }} open={openDropdown === 'ta2'} onToggle={setOpenDropdown} disabled={isFieldHeadView || isFieldDirectorView} />
                <FilterDropdown id="diseaseArea" label="Disease Area" icon={Leaf} options={diseaseAreaOptions} value={filterDiseaseArea} onChange={value => { trackFilterChange('disease-area', value); setFilterDiseaseArea(value); }} open={openDropdown === 'diseaseArea'} onToggle={setOpenDropdown} disabled={isFieldHeadView || isFieldDirectorView} />
              </div>
            </div>

            {/* Organization */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', minWidth: 78, paddingTop: 6 }}>Organization</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, flex: 1 }}>
                <FilterDropdown id="fieldHead" label="Field Head" icon={Building2} options={fieldHeadOptions} value={effectiveFieldHeadWwid}
                  onChange={v => { trackFilterChange('field-head', v ? 'selected' : 'all'); setFilterFieldHead(v); setFilterFieldDirector(null); setFilterMsl(null); }}
                  open={openDropdown === 'fieldHead'} onToggle={setOpenDropdown} disabled={isFieldHeadView || isFieldDirectorView} />
                <FilterDropdown id="fieldDirector" label="Field Director" icon={User} options={fieldDirectorOptions} value={filterFieldDirector}
                  onChange={v => { trackFilterChange('field-director', v ? 'selected' : 'all'); setFilterFieldDirector(v); setFilterMsl(null); }}
                  open={openDropdown === 'fieldDirector'} onToggle={setOpenDropdown} disabled={isFieldDirectorView} />
                <FilterDropdown id="msl" label="MSL" icon={Users} options={mslOptions} value={filterMsl} onChange={value => { trackFilterChange('msl', value ? 'selected' : 'all'); setFilterMsl(value); }} open={openDropdown === 'msl'} onToggle={setOpenDropdown} />
                <FilterDropdown id="jobRole" label="Job Role" icon={Briefcase} options={jobRoleOptions} value={filterJobRole} onChange={value => { trackFilterChange('job-role', value); setFilterJobRole(value); }} open={openDropdown === 'jobRole'} onToggle={setOpenDropdown} disabled={isFieldDirectorView} />
                {/* Bug 1 fix: always show the selected MSL's name + REAL FCR count
                    (0, 1, or more) — never falls back to TA/Disease Area. */}
                {filterMsl && (
                  <button
                    onMouseDown={() => {
                      telemetry.trackButtonClick('dashboard-open-msl-fcr-list', 'Open MSL FCR list', { page: 'dashboard' });
                      setFcrListPanel({
                      title: mslOptions.find(o => o.value === filterMsl)?.label || filterMsl,
                      subtitle: 'MSL',
                      queryParams: buildActiveFilterParams(),
                      });
                    }}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
                      padding: '8px 10px', border: '1px solid #EEE7E8', borderRadius: 8,
                      background: '#fff', cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left',
                    }}
                  >
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#1A1A1A', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {mslOptions.find(o => o.value === filterMsl)?.label || filterMsl}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
                      <span style={{ fontSize: 13, fontWeight: 800, color: '#D71600' }}>
                        {summaryLoading ? '…' : fmt(kpi?.total_fcrs)}
                      </span>
                      <span style={{ fontSize: 10, color: '#9CA3AF', fontWeight: 600 }}>FCR{kpi?.total_fcrs === 1 ? '' : 's'}</span>
                    </span>
                  </button>
                )}
              </div>
            </div>

            {/* Geography */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', minWidth: 78, paddingTop: 6 }}>Geography</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, flex: 1 }}>
                <FilterDropdown id="region2" label="Region" icon={MapPin} options={regionOptions} value={filterRegion} onChange={value => { trackFilterChange('region', value); setFilterRegion(value); }} open={openDropdown === 'region2'} onToggle={setOpenDropdown} disabled={isFieldDirectorView} />
                <FilterDropdown id="territory" label="Territory" icon={MapIcon} options={territoryOptions} value={filterTerritory} onChange={value => { trackFilterChange('territory', value ? 'selected' : 'all'); setFilterTerritory(value); }} open={openDropdown === 'territory'} onToggle={setOpenDropdown} disabled={isFieldDirectorView} />
                {/* Bug 2 fix: always show the selected Region's REAL FCR count
                    and a clickable list of the FCRs published there — never
                    falls back to TA/Disease Area data. */}
                {filterRegion && (
                  <button
                    onMouseDown={() => {
                      telemetry.trackButtonClick('dashboard-open-region-fcr-list', 'Open region FCR list', { page: 'dashboard' });
                      setFcrListPanel({
                      title: filterRegion,
                      subtitle: 'Region',
                      queryParams: buildActiveFilterParams(),
                      });
                    }}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8,
                      padding: '8px 10px', border: '1px solid #EEE7E8', borderRadius: 8,
                      background: '#fff', cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left',
                    }}
                  >
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#1A1A1A', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {filterRegion}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
                      <span style={{ fontSize: 13, fontWeight: 800, color: '#D71600' }}>
                        {summaryLoading ? '…' : fmt(kpi?.total_fcrs)}
                      </span>
                      <span style={{ fontSize: 10, color: '#9CA3AF', fontWeight: 600 }}>FCR{kpi?.total_fcrs === 1 ? '' : 's'}</span>
                    </span>
                  </button>
                )}
              </div>
            </div>

            {/* FCR */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', minWidth: 78, paddingTop: 6 }}>FCR</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, flex: 1 }}>
                <FilterDropdown id="trainingNeeded" label="Training Needed" icon={GraduationCap} options={TRAINING_NEEDED_OPTIONS} value={filterTrainingNeeded} onChange={value => { trackFilterChange('training-needed', value); setFilterTrainingNeeded(value); }} open={openDropdown === 'trainingNeeded'} onToggle={setOpenDropdown} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── CHOOSE A VIEW ── */}
      <div>
        <div className="section-eyebrow" style={{ marginBottom: 10 }}>Choose a View</div>
        <div className="view-cards-grid">
          <ViewCard num={1} icon={Activity} title="Coaching Coverage & Cadence" sub="Reach, cadence & completion" active={activeView === 0} onClick={() => { telemetry.trackButtonClick('dashboard-view-coverage', 'Coaching Coverage & Cadence', { eventName: 'summary_view_coaching_coverage_selected', page: 'dashboard', view: 'coaching_coverage_cadence', viewNum: 1 }); setActiveView(0); }} />
          <ViewCard num={2} icon={Target} title="Training & Skill Gaps" sub="Where coaching should focus" active={activeView === 1} onClick={() => { telemetry.trackButtonClick('dashboard-view-training', 'Training & Skill Gaps', { eventName: 'summary_view_training_skill_gaps_selected', page: 'dashboard', view: 'training_skill_gaps', viewNum: 2 }); setActiveView(1); }} />
          <ViewCard num={3} icon={Sparkles} title="Skill Proficiency Trend" sub="Score trends over time" active={activeView === 2} onClick={() => { telemetry.trackButtonClick('dashboard-view-skill-trend', 'Skill Proficiency Trend', { eventName: 'summary_view_skill_proficiency_trend_selected', page: 'dashboard', view: 'skill_proficiency_trend', viewNum: 3 }); setActiveView(2); }} />
        </div>
      </div>

      {/* ── DATA SECTION: view 0 (Coverage) ── */}
      {activeView === 1 && (
        <TrainingSkillGapsView
          onOpenFcr={onOpenFcr}
          filterTA={filterTA}
          filterTimeframe={filterTimeframe}
          filterRegion={filterRegion}
          filterDiseaseArea={filterDiseaseArea}
          customFrom={customFrom}
          customTo={customTo}
        />
      )}
      {activeView === 2 && (
        <SkillProficiencyTrendView
          filterTA={filterTA}
          filterTimeframe={filterTimeframe}
          filterRegion={filterRegion}
          filterDiseaseArea={filterDiseaseArea}
          customFrom={customFrom}
          customTo={customTo}
        />
      )}
      {activeView === 0 && <div className="dash-card">
        {/* Toggle row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10, flexWrap: 'wrap', gap: 8 }}>
          <button className="all-pill" onClick={() => telemetry.trackButtonClick('summary-chart-all', 'All', { eventName: 'summary_chart_all_pill_clicked', page: 'summary', view: 'coaching_coverage_cadence' })}>🏠 All</button>
        </div>

        {/* Charts row */}
        <div className="charts-grid">

          {/* Bar chart */}
          <div className="chart-card">
            <div className="chart-card-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ width: 3, height: 16, background: '#D71600', borderRadius: 2 }} />
                {isDrilledDown && !isFieldHeadHomeLevel && !isFieldDirectorView && (
                  <button
                    onClick={handleBack}
                    style={{ display: 'flex', alignItems: 'center', gap: 2, border: 'none', background: 'transparent', cursor: 'pointer', padding: 0, color: '#6B7280', fontSize: 12 }}
                  >
                    <ChevronDown size={12} style={{ transform: 'rotate(90deg)' }} /> Back
                  </button>
                )}
                <span style={{ fontSize: 13, fontWeight: 700, color: '#1A1A1A' }}>{barChartLabel}</span>
              </div>
              <span style={{ fontSize: 10, color: '#9CA3AF' }}>
                {isDrilledIntoMsls ? (fdRepsLoading ? 'loading…' : '')
                  : isDrilledIntoFDs ? (fdLoading ? 'loading…' : 'click to drill in')
                  : isDrilledDown ? 'click to drill in'
                  : (regionToggle === 'ta' ? 'click to drill in' : '')}
              </span>
            </div>
            {isDrilledIntoMsls ? (
              <MslTeamList
                reps={fdReps}
                loading={fdRepsLoading}
                onSelectRep={(r) => {
                  telemetry.trackCustomEvent('rep_drilldown_opened', { page: 'dashboard', source: 'field-director-team' });
                  const [first, ...rest] = (r.name || '').split(' ');
                  setSelectedMslRep({
                    rep_wwid: r.wwid,
                    first_nm: first || r.name,
                    last_nm:  rest.join(' '),
                    desig:    r.job_title,
                    ta:       selectedDisease,
                    region:   selectedFD?.region,
                  });
                }}
              />
            ) : (
            <ResponsiveContainer width="100%" height={isDrilledDown ? 315 : 290}>
              <BarChart data={barChartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }} barCategoryGap="18%">
                <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                <XAxis
                  dataKey="region"
                  tick={
                    isDrilledIntoFDs ? <FDAxisTick data={barChartData} />
                    : isDrilledDown  ? <DiseaseAxisTick data={barChartData} />
                    : { fontSize: 12, fill: '#6B7280' }
                  }
                  axisLine={false}
                  tickLine={false}
                  interval={0}
                  height={isDrilledDown ? 42 : 30}
                />
                <YAxis domain={barChartAxis.domain} ticks={barChartAxis.ticks} allowDecimals={false} tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} width={40} />
                <Tooltip content={isDrilledIntoFDs ? <FDBarTip /> : <BarTip />} cursor={{ fill: '#FEF2F2' }} />
                <Bar
                  dataKey="count"
                  fill="#D71600"
                  radius={[8, 8, 0, 0]}
                  maxBarSize={64}
                  onClick={handleBarClick}
                  style={{ cursor: (regionToggle === 'ta' && !isDrilledIntoFDs) ? 'pointer' : (isDrilledIntoFDs && !isDrilledIntoMsls ? 'pointer' : 'default') }}
                />
              </BarChart>
            </ResponsiveContainer>
            )}
          </div>

          {/* FCR Completion vs. Required Base — stacked coverage chart */}
          <div className="chart-card">
            <div className="chart-card-header" style={{ flexWrap: 'wrap', gap: 8 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: '#1A1A1A' }}>FCR Completion vs. Required Base</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className={isTrendingUp ? 'positive-pill' : 'trending-pill'}>{isTrendingUp ? '📈 Trending up' : '📉 Trending down'}</span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={290}>
              <BarChart data={fcrsTrend} margin={{ top: 12, right: 12, left: 0, bottom: 0 }} barCategoryGap="28%">
                <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
                <XAxis
                  dataKey="quarter"
                  tick={<CoverageAxisTick data={fcrsTrend} />}
                  axisLine={false}
                  tickLine={false}
                  interval={0}
                  height={40}
                />
                <YAxis domain={coverageAxis.domain} ticks={coverageAxis.ticks} allowDecimals={false} tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} width={40} />
                <Tooltip content={<CoverageTip />} cursor={{ fill: '#FEF2F2' }} />
                {requiredFcrs > 0 && (
                  <ReferenceLine
                    y={requiredFcrs}
                    stroke="#9CA3AF"
                    strokeDasharray="5 4"
                    strokeWidth={2}
                    label={{ value: `Required ${fmt(requiredFcrs)}`, position: 'insideTopLeft', fill: '#9CA3AF', fontSize: 10, offset: 10 }}
                  />
                )}
                <Bar dataKey="coached" stackId="coverage" fill="#D71600" radius={[0, 0, 0, 0]} maxBarSize={56} />
                <Bar dataKey="repeats" stackId="coverage" fill="#D71600" fillOpacity={0.28} radius={[4, 4, 0, 0]} maxBarSize={56} />
              </BarChart>
            </ResponsiveContainer>
            <div className="chart-legend-row">
              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
                <span className="legend-item">
                  <span style={{ width: 10, height: 10, background: '#D71600', borderRadius: 2, display: 'inline-block' }} />
                  MSLs coached (distinct)
                </span>
                <span className="legend-item">
                  <span style={{ width: 10, height: 10, background: '#D71600', opacity: 0.28, borderRadius: 2, display: 'inline-block' }} />
                  Repeat observations
                </span>
                <span className="legend-item" style={{ color: '#9CA3AF' }}>
                  <span style={{ width: 10, borderTop: '2px dashed #9CA3AF', display: 'inline-block' }} />
                  Required base (1 per MSL per quarter{requiredFcrs ? ` = ${fmt(requiredFcrs)}` : ''})
                </span>
              </div>
              <span className={isAheadOfPace ? 'positive-pill' : 'trending-pill'}>{isAheadOfPace ? `+${paceGap}` : paceGap} total FCRs vs required base</span>
            </div>
          </div>

        </div>
      </div>}

      {/* ═══ MSL -> FCR drill-down (from the Field Director level-4 list) ═══ */}
      <RepFcrDrilldown rep={selectedMslRep} onClose={() => setSelectedMslRep(null)} />

      {/* ═══ "More filters" FCR list panel (Bug 1: MSL, Bug 2: Region) ═══ */}
      {fcrListPanel && (
        <FilteredFcrListPanel
          title={fcrListPanel.title}
          subtitle={fcrListPanel.subtitle}
          queryParams={fcrListPanel.queryParams}
          onClose={() => setFcrListPanel(null)}
        />
      )}

      {/* ═══ AI Digest ═══ */}
      <AIDigestButton onClick={() => { telemetry.trackButtonClick('btn-ai-digest-trigger', 'AI Digest', { page: 'summary' }); setAiDigestOpen(true); }} />
      <AIDigestPanel
        open={aiDigestOpen}
        onClose={() => setAiDigestOpen(false)}
        scope={aiDigestScope}
        onDeepLink={(deepLink) => onDigestNavigate?.(deepLink)}
      />
    </div>
  );
}
