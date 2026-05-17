import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, Cell
} from 'recharts'
import { useReviewStore } from '../../store/reviewStore'
import clsx from 'clsx'

/* ── Sentiment config ───────────────────────────────────────────────────── */
const SENTIMENT_CONFIG = {
  positive:  { label: 'Positive',  color: '#28C76F', bg: '#DCFCE7', border: '#BBF7D0', emoji: '😊', badgeClass: 'badge-positive',  icon: '✅' },
  negative:  { label: 'Negative',  color: '#EA5455', bg: '#FEE2E2', border: '#FECACA', emoji: '😠', badgeClass: 'badge-negative',  icon: '❌' },
  neutral:   { label: 'Neutral',   color: '#FFB547', bg: '#FEF3C7', border: '#FDE68A', emoji: '😐', badgeClass: 'badge-neutral',   icon: '➖' },
  mixed:     { label: 'Mixed',     color: '#F7936F', bg: '#FFF1E6', border: '#FED7AA', emoji: '🔀', badgeClass: 'badge-mixed',     icon: '🔀' },
  sarcastic: { label: 'Sarcastic', color: '#A78BFA', bg: '#EDE9FE', border: '#DDD6FE', emoji: '😏', badgeClass: 'badge-sarcastic', icon: '😏' },
  ambiguous: { label: 'Ambiguous', color: '#60A5FA', bg: '#DBEAFE', border: '#BFDBFE', emoji: '❓', badgeClass: 'badge-ambiguous', icon: '❓' },
}

/* ── Custom tooltip ─────────────────────────────────────────────────────── */
const ChartTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-3 py-2.5 rounded-xl text-xs border"
      style={{ background: '#FFFFFF', borderColor: '#E5E7EB', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
      {payload.map(p => (
        <div key={p.name} className="flex items-center gap-2 mb-0.5">
          <div className="w-2 h-2 rounded-full" style={{ background: p.stroke || p.fill }} />
          <span style={{ color: '#64748B' }}>{p.name}:</span>
          <span className="font-bold" style={{ color: '#1E293B' }}>{p.value}%</span>
        </div>
      ))}
    </div>
  )
}

/* ── Feature card ───────────────────────────────────────────────────────── */
function FeatureCard({ feature, data, selected, onClick }) {
  const dominant = data.positive > data.negative ? 'positive' : data.negative > data.positive ? 'negative' : 'neutral'
  const cfg = SENTIMENT_CONFIG[dominant] || SENTIMENT_CONFIG.neutral

  return (
    <motion.div
      whileHover={{ y: -3 }}
      onClick={onClick}
      className="card-3d-sm p-4 cursor-pointer transition-all"
      style={selected ? { borderColor: '#FF7A00', background: '#FFF7ED', boxShadow: '0 0 0 2px rgba(255,122,0,0.15)' } : {}}
    >
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-semibold text-xs capitalize leading-tight" style={{ color: '#1E293B' }}>
          {feature.replace(/_/g, ' ')}
        </h4>
        <span className={`sentiment-badge ${cfg.badgeClass} flex-shrink-0 ml-1`}>
          {cfg.emoji} {cfg.label}
        </span>
      </div>

      {/* Praise bar */}
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-xs w-14 text-right font-medium" style={{ color: '#28C76F' }}>
          {Math.round(data.praise_rate * 100)}%
        </span>
        <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
          <div className="h-full rounded-full" style={{ width: `${data.praise_rate * 100}%`, background: '#28C76F' }} />
        </div>
        <span className="text-xs w-10" style={{ color: '#94A3B8' }}>👍</span>
      </div>
      {/* Complaint bar */}
      <div className="flex items-center gap-2">
        <span className="text-xs w-14 text-right font-medium" style={{ color: '#EA5455' }}>
          {Math.round(data.complaint_rate * 100)}%
        </span>
        <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
          <div className="h-full rounded-full" style={{ width: `${data.complaint_rate * 100}%`, background: '#EA5455' }} />
        </div>
        <span className="text-xs w-10" style={{ color: '#94A3B8' }}>👎</span>
      </div>

      <div className="mt-2 text-xs" style={{ color: '#94A3B8' }}>
        {data.total_mentions} mentions · {Math.round(data.avg_confidence * 100)}% confidence
      </div>
    </motion.div>
  )
}

/* ── Feature detail panel ───────────────────────────────────────────────── */
function FeatureDetail({ feature, data }) {
  const sentimentData = [
    { name: 'Positive',  value: data.positive  || 0, color: '#28C76F', bg: '#DCFCE7' },
    { name: 'Negative',  value: data.negative  || 0, color: '#EA5455', bg: '#FEE2E2' },
    { name: 'Neutral',   value: data.neutral   || 0, color: '#FFB547', bg: '#FEF3C7' },
    { name: 'Mixed',     value: data.mixed     || 0, color: '#F7936F', bg: '#FFF1E6' },
    { name: 'Sarcastic', value: data.sarcastic || 0, color: '#A78BFA', bg: '#EDE9FE' },
    { name: 'Ambiguous', value: data.ambiguous || 0, color: '#60A5FA', bg: '#DBEAFE' },
  ].filter(d => d.value > 0)

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="card-3d p-6 h-full"
    >
      <h3 className="font-semibold text-base capitalize mb-1" style={{ color: '#1E293B' }}>
        {feature.replace(/_/g, ' ')} — Detail
      </h3>
      <p className="text-xs mb-5" style={{ color: '#94A3B8' }}>
        {data.total_mentions} total mentions · Avg confidence: {Math.round(data.avg_confidence * 100)}%
      </p>

      <div className="grid grid-cols-2 gap-6 mb-5">
        {/* Sentiment split */}
        <div>
          <div className="text-xs font-semibold mb-3" style={{ color: '#475569' }}>All Sentiment Types</div>
          {sentimentData.map(d => (
            <div key={d.name} className="flex items-center gap-2 mb-2.5">
              <div className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 text-xs"
                style={{ background: d.bg }}>
                {SENTIMENT_CONFIG[d.name.toLowerCase()]?.emoji}
              </div>
              <span className="text-xs flex-1" style={{ color: '#475569' }}>{d.name}</span>
              <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
                <div className="h-full rounded-full"
                  style={{ width: `${data.total_mentions ? d.value / data.total_mentions * 100 : 0}%`, background: d.color }} />
              </div>
              <span className="text-xs font-bold w-6 text-right" style={{ color: d.color }}>{d.value}</span>
            </div>
          ))}
        </div>
        {/* Rate summary */}
        <div>
          <div className="text-xs font-semibold mb-3" style={{ color: '#475569' }}>Rate Summary</div>
          {[
            { label: 'Complaint Rate', val: Math.round(data.complaint_rate * 100), color: '#EA5455', bg: '#FEE2E2' },
            { label: 'Praise Rate',    val: Math.round(data.praise_rate    * 100), color: '#28C76F', bg: '#DCFCE7' },
            { label: 'Avg Confidence', val: Math.round(data.avg_confidence * 100), color: '#2563EB', bg: '#DBEAFE' },
          ].map(({ label, val, color, bg }) => (
            <div key={label} className="mb-3">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs" style={{ color: '#64748B' }}>{label}</span>
                <span className="text-sm font-bold" style={{ color }}>{val}%</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${val}%` }}
                  transition={{ duration: 0.7 }}
                  className="h-full rounded-full"
                  style={{ background: color }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Excerpts */}
      {data.top_excerpts?.length > 0 && (
        <div>
          <div className="text-xs font-semibold mb-2" style={{ color: '#475569' }}>Sample Excerpts</div>
          <div className="space-y-2">
            {data.top_excerpts.slice(0, 4).map((ex, i) => (
              <div key={i} className="px-3 py-2 rounded-xl text-xs italic"
                style={{ background: '#F8FAFC', border: '1px solid #E5E7EB', color: '#64748B' }}>
                "{ex}"
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rep reviews */}
      {data.representative_reviews?.length > 0 && (
        <div className="mt-4">
          <div className="text-xs font-semibold mb-2" style={{ color: '#475569' }}>Representative Reviews</div>
          <div className="space-y-2">
            {data.representative_reviews.slice(0, 3).map((r, i) => {
              const cfg = SENTIMENT_CONFIG[r.sentiment] || SENTIMENT_CONFIG.neutral
              return (
                <div key={i} className="px-3 py-2.5 rounded-xl text-xs"
                  style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
                  <div className="font-semibold mb-0.5 capitalize flex items-center gap-1.5"
                    style={{ color: cfg.color }}>
                    {cfg.emoji} {r.sentiment}
                  </div>
                  <div style={{ color: '#475569' }}>{r.excerpt}…</div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </motion.div>
  )
}

/* ── Main SentimentTab ───────────────────────────────────────────────────── */
export default function SentimentTab() {
  const { report, getFeatureSummaryData, getSentimentTypeCounts } = useReviewStore()
  const [selectedFeature, setSelectedFeature] = useState(null)
  const featureData = getFeatureSummaryData()
  const sentCounts  = getSentimentTypeCounts()

  if (!report) return null

  const radarData = featureData.slice(0, 7).map(d => ({
    feature: d.feature.length > 12 ? d.feature.slice(0, 12) + '…' : d.feature,
    complaints: d.complaints,
    praises:    d.praises,
  }))

  const selectedData = selectedFeature ? report.feature_summary[selectedFeature] : null

  // All 6 sentiment types — total clean
  const totalClean = report.clean_reviews || 1

  return (
    <div className="space-y-6">

      {/* ── All 5+ Sentiment Types summary ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-3d p-6"
      >
        <h3 className="section-header mb-1">All Sentiment Components</h3>
        <p className="text-xs mb-5" style={{ color: '#94A3B8' }}>
          Complete breakdown across all {Object.keys(SENTIMENT_CONFIG).length} sentiment categories
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(SENTIMENT_CONFIG).map(([key, cfg]) => {
            const count = sentCounts[key] || 0
            const pct   = Math.round((count / totalClean) * 100)
            return (
              <motion.div
                key={key}
                whileHover={{ y: -4 }}
                className="rounded-2xl p-4 text-center"
                style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
              >
                <div className="text-3xl mb-2">{cfg.emoji}</div>
                <div className="text-2xl font-bold" style={{ color: cfg.color }}>{count}</div>
                <div className="text-xs font-bold mt-0.5" style={{ color: cfg.color }}>{cfg.label}</div>
                <div className="text-xs mt-1" style={{ color: '#94A3B8' }}>{pct}% of reviews</div>
                {/* Mini bar */}
                <div className="mt-2 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.6)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.8, delay: 0.1 }}
                    className="h-full rounded-full"
                    style={{ background: cfg.color }}
                  />
                </div>
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* ── Radar + Feature Detail ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-3d p-6 lg:col-span-1">
          <h3 className="section-header">Feature Radar</h3>
          <p className="section-subtext">Top features by complaint & praise rate</p>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#E5E7EB" />
              <PolarAngleAxis dataKey="feature" tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <Radar name="Complaints%" dataKey="complaints" stroke="#EA5455" fill="#EA5455" fillOpacity={0.12} strokeWidth={2} />
              <Radar name="Praises%"    dataKey="praises"    stroke="#28C76F" fill="#28C76F" fillOpacity={0.12} strokeWidth={2} />
              <Tooltip content={<ChartTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
          <div className="flex items-center gap-4 justify-center">
            {[{ color: '#EA5455', label: 'Complaints' }, { color: '#28C76F', label: 'Praises' }].map(({ color, label }) => (
              <div key={label} className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full" style={{ background: color }} />
                <span className="text-xs" style={{ color: '#64748B' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            {selectedData ? (
              <FeatureDetail key={selectedFeature} feature={selectedFeature} data={selectedData} />
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="card-3d p-8 h-full flex items-center justify-center text-center"
                style={{ minHeight: 320 }}
              >
                <div>
                  <div className="text-5xl mb-4">👈</div>
                  <p className="text-sm font-medium" style={{ color: '#64748B' }}>
                    Click a feature card to see detailed sentiment breakdown
                  </p>
                  <p className="text-xs mt-1" style={{ color: '#94A3B8' }}>
                    Including all 6 sentiment components per feature
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── Feature cards grid ── */}
      <div>
        <h3 className="section-header mb-4">All Product Features ({featureData.length})</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {featureData.map(({ feature }) => (
            <FeatureCard
              key={feature}
              feature={feature}
              data={report.feature_summary[feature.replace(/ /g, '_')] || report.feature_summary[feature] || {}}
              selected={selectedFeature === feature}
              onClick={() => setSelectedFeature(selectedFeature === feature ? null : feature)}
            />
          ))}
        </div>
      </div>

      {/* ── Special Categories ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Sarcastic Reviews',  key: 'sarcastic',    cfg: SENTIMENT_CONFIG.sarcastic, desc: 'Flagged for human review — sentiment is likely inverted' },
          { label: 'Ambiguous Reviews',  key: 'ambiguous',    cfg: SENTIMENT_CONFIG.ambiguous, desc: 'Unclear intent — not forced into positive/negative' },
          { label: 'Multilingual Reviews', key: 'multilingual', cfg: { color: '#0891B2', bg: '#ECFEFF', border: '#A5F3FC', emoji: '🌍' }, desc: 'Hindi, Hinglish, or other Indian languages detected' },
        ].map(({ label, key, cfg, desc }) => {
          const count = key === 'multilingual'
            ? (report.processed_reviews?.filter(r => r.flags?.includes(key)).length || 0)
            : (sentCounts[key] || 0)
          return (
            <motion.div
              key={key}
              whileHover={{ y: -3 }}
              className="card-3d-sm p-5"
              style={{ background: cfg.bg, borderColor: cfg.border }}
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-2xl">{cfg.emoji}</span>
                <div>
                  <div className="text-2xl font-bold" style={{ color: cfg.color }}>{count}</div>
                  <div className="text-sm font-semibold" style={{ color: '#1E293B' }}>{label}</div>
                </div>
              </div>
              <div className="text-xs" style={{ color: '#64748B' }}>{desc}</div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
