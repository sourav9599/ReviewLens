import { motion } from 'framer-motion'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { useReviewStore } from '../../store/reviewStore'
import {
  AlertTriangle, TrendingUp, CheckCircle, Brain,
  Shield, MessageSquare, Smile, Repeat, ThumbsUp, ThumbsDown,
  Package
} from 'lucide-react'

/* ── Sentiment meta ───────────────────────────────────────────────────────── */
const SENTIMENT_CONFIG = {
  positive:  { label: 'Positive',  color: '#28C76F', bg: '#DCFCE7', border: '#BBF7D0', emoji: '😊' },
  negative:  { label: 'Negative',  color: '#EA5455', bg: '#FEE2E2', border: '#FECACA', emoji: '😠' },
  neutral:   { label: 'Neutral',   color: '#FFB547', bg: '#FEF3C7', border: '#FDE68A', emoji: '😐' },
  mixed:     { label: 'Mixed',     color: '#F7936F', bg: '#FFF1E6', border: '#FED7AA', emoji: '🔀' },
  sarcastic: { label: 'Sarcastic', color: '#A78BFA', bg: '#EDE9FE', border: '#DDD6FE', emoji: '😏' },
  ambiguous: { label: 'Ambiguous', color: '#60A5FA', bg: '#DBEAFE', border: '#BFDBFE', emoji: '❓' },
}

/* ── Custom chart tooltips ───────────────────────────────────────────────── */
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-4 py-3 rounded-xl text-xs border"
      style={{ background: '#FFFFFF', borderColor: '#E5E7EB', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
      {label && <div className="font-semibold mb-1.5" style={{ color: '#1E293B' }}>{label}</div>}
      {payload.map(p => (
        <div key={p.dataKey} className="flex items-center gap-2 mb-0.5">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color || p.fill }} />
          <span style={{ color: '#64748B' }}>{p.name || p.dataKey}:</span>
          <span className="font-semibold" style={{ color: '#1E293B' }}>{p.value}%</span>
        </div>
      ))}
    </div>
  )
}

const PieTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-4 py-3 rounded-xl text-xs border"
      style={{ background: '#FFFFFF', borderColor: '#E5E7EB', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
      <div className="font-semibold capitalize" style={{ color: '#1E293B' }}>{payload[0].name}</div>
      <div className="font-bold text-lg" style={{ color: payload[0].payload.color }}>{payload[0].value}%</div>
    </div>
  )
}

/* ── Product Satisfaction Card ─────────────────────────────────────────────── */
function ProductSatisfactionSection() {
  const { getProductSatisfactionData } = useReviewStore()
  const products = getProductSatisfactionData()

  if (!products.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="card-3d p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: '#FFF3E8', border: '1px solid #FED7AA' }}>
          <Package size={16} style={{ color: '#FF7A00' }} />
        </div>
        <div>
          <h3 className="section-header mb-0">Product Satisfaction Analysis</h3>
          <p className="text-xs" style={{ color: '#94A3B8' }}>
            Per-product satisfied vs. unsatisfied users — based on review sentiment
          </p>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-5">
        {[
          { label: 'Satisfied',   color: '#28C76F', sub: 'positive + neutral' },
          { label: 'Unsatisfied', color: '#EA5455', sub: 'negative + mixed + sarcastic + ambiguous' },
        ].map(({ label, color, sub }) => (
          <div key={label} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm" style={{ background: color }} />
            <span className="text-xs font-medium" style={{ color: '#1E293B' }}>{label}</span>
            <span className="text-xs hidden sm:inline" style={{ color: '#94A3B8' }}>({sub})</span>
          </div>
        ))}
      </div>

      {/* Per-product bars */}
      <div className="space-y-4">
        {products.map((p, i) => (
          <motion.div
            key={p.product}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.55 + i * 0.06 }}
          >
            {/* Product name row */}
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-semibold truncate max-w-xs" style={{ color: '#1E293B' }}>
                  {p.product}
                </span>
                <span className="text-xs px-1.5 py-0.5 rounded-full"
                  style={{ background: '#F1F5F9', color: '#64748B' }}>
                  {p.total} reviews
                </span>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="text-xs font-bold" style={{ color: '#28C76F' }}>
                  <ThumbsUp size={10} className="inline mr-0.5" />
                  {p.satisfiedRate}%
                </span>
                <span className="text-xs font-bold" style={{ color: '#EA5455' }}>
                  <ThumbsDown size={10} className="inline mr-0.5" />
                  {p.unsatisfiedRate}%
                </span>
              </div>
            </div>

            {/* Stacked bar */}
            <div className="h-3 rounded-full overflow-hidden flex"
              style={{ background: '#F1F5F9', border: '1px solid #E5E7EB' }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${p.satisfiedRate}%` }}
                transition={{ duration: 0.9, delay: 0.6 + i * 0.07, ease: 'easeOut' }}
                className="h-full"
                style={{
                  background: 'linear-gradient(90deg, #28C76F, #4ADE80)',
                  borderRadius: p.satisfiedRate >= 100 ? '99px' : '99px 0 0 99px',
                }}
              />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${p.unsatisfiedRate}%` }}
                transition={{ duration: 0.9, delay: 0.7 + i * 0.07, ease: 'easeOut' }}
                className="h-full"
                style={{
                  background: 'linear-gradient(90deg, #EA5455, #F87171)',
                  borderRadius: p.satisfiedRate === 0 ? '99px' : '0 99px 99px 0',
                }}
              />
            </div>

            {/* Sentiment breakdown chips */}
            <div className="flex flex-wrap gap-1.5 mt-2">
              {Object.entries(p.sentiments || {}).map(([sent, count]) => {
                const cfg = SENTIMENT_CONFIG[sent]
                if (!cfg || count === 0) return null
                return (
                  <span key={sent}
                    className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium"
                    style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }}>
                    {cfg.emoji} {cfg.label}: {count}
                  </span>
                )
              })}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}

/* ── Main OverviewTab ─────────────────────────────────────────────────────── */
export default function OverviewTab() {
  const {
    report, getSentimentPieData, getFeatureSummaryData,
    getEmojiData, getBotRiskData, getOrchestratorData, getSentimentTypeCounts
  } = useReviewStore()
  if (!report) return null

  const pieData       = getSentimentPieData()
  const featureData   = getFeatureSummaryData().slice(0, 8)
  const criticalAlerts = report.trend_alerts?.filter(a => a.severity === 'critical') || []
  const topRec        = report.recommendations?.[0]
  const agentTrace    = report.agent_trace || []
  const emojiData     = getEmojiData()
  const botData       = getBotRiskData()
  const { decisions, feedbackLoops } = getOrchestratorData()
  const sentimentCounts = getSentimentTypeCounts()

  const statCards = [
    { icon: MessageSquare, label: 'Total Reviews',  val: report.total_reviews,             sub: `${report.clean_reviews} clean`,          gradient: 'stat-gradient-blue',   iconBg: '#DBEAFE', iconColor: '#2563EB' },
    { icon: Shield,        label: 'Bots Detected',  val: report.bot_suspected_count,        sub: `${botData?.botRate || 0}% of total`,     gradient: 'stat-gradient-red',    iconBg: '#FEE2E2', iconColor: '#DC2626' },
    { icon: Smile,         label: 'Emojis Detected', val: emojiData?.total_emojis_found || 0, sub: `${emojiData?.reviews_with_emojis || 0} reviews`, gradient: 'stat-gradient-yellow', iconBg: '#FEF3C7', iconColor: '#D97706' },
    { icon: TrendingUp,    label: 'Trend Alerts',   val: report.trend_alerts?.length || 0, sub: `${criticalAlerts.length} critical`,       gradient: 'stat-gradient-orange', iconBg: '#FFF1E6', iconColor: '#FF7A00' },
  ]

  return (
    <div className="space-y-6">

      {/* ── Critical alerts banner ── */}
      {criticalAlerts.length > 0 && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          {criticalAlerts.map(alert => (
            <div key={alert.alert_id}
              className="rounded-2xl p-4 flex items-start gap-3 mb-3 border alert-critical">
              <AlertTriangle size={17} style={{ color: '#DC2626', flexShrink: 0 }} className="mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-semibold" style={{ color: '#DC2626' }}>
                  Critical: {alert.feature.replace(/_/g, ' ').toUpperCase()} — {alert.alert_type.replace(/_/g, ' ')}
                </div>
                <div className="text-xs mt-0.5" style={{ color: '#64748B' }}>{alert.description}</div>
              </div>
              <div className="text-right flex-shrink-0">
                <div className="text-lg font-bold" style={{ color: '#DC2626' }}>+{alert.change_percent}%</div>
                <div className="text-xs" style={{ color: '#94A3B8' }}>change</div>
              </div>
            </div>
          ))}
        </motion.div>
      )}

      {/* ── Stats row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ icon: Icon, label, val, sub, gradient, iconBg, iconColor }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className={`stat-card ${gradient}`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: iconBg }}>
                <Icon size={16} style={{ color: iconColor }} />
              </div>
            </div>
            <div className="font-bold text-3xl" style={{ color: '#1E293B', fontFamily: 'DM Sans, sans-serif' }}>{val}</div>
            <div className="text-xs font-semibold" style={{ color: '#475569' }}>{label}</div>
            <div className="text-xs" style={{ color: '#94A3B8' }}>{sub}</div>
          </motion.div>
        ))}
      </div>

      {/* ── Sentiment Type Breakdown Row ── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card-3d p-5"
      >
        <h3 className="section-header mb-4">Review Sentiment Types</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {Object.entries(SENTIMENT_CONFIG).map(([key, cfg]) => {
            const count = sentimentCounts[key] || 0
            const total = report.clean_reviews || 1
            const pct = Math.round((count / total) * 100)
            return (
              <div key={key} className="rounded-xl p-3 text-center"
                style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
                <div className="text-2xl mb-1">{cfg.emoji}</div>
                <div className="text-lg font-bold" style={{ color: cfg.color }}>{count}</div>
                <div className="text-xs font-semibold" style={{ color: cfg.color }}>{cfg.label}</div>
                <div className="text-xs mt-0.5" style={{ color: '#94A3B8' }}>{pct}%</div>
              </div>
            )
          })}
        </div>
      </motion.div>

      {/* ── Charts row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Sentiment Pie */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.25 }}
          className="card-3d p-6 lg:col-span-2"
        >
          <h3 className="section-header">Overall Sentiment</h3>
          <p className="section-subtext">Distribution across clean reviews</p>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={52}
                outerRadius={82}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<PieTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-x-4 gap-y-1.5 justify-center mt-2">
            {pieData.map(d => (
              <div key={d.name} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                <span className="text-xs capitalize font-medium" style={{ color: '#475569' }}>
                  {d.name} <span style={{ color: '#94A3B8' }}>({d.value}%)</span>
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Feature Bar Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.32 }}
          className="card-3d p-6 lg:col-span-3"
        >
          <h3 className="section-header">Feature Sentiment Breakdown</h3>
          <p className="section-subtext">Complaint vs praise rate per product attribute (%)</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={featureData} barSize={10} barGap={2}>
              <XAxis dataKey="feature" tick={{ fontSize: 10, fill: '#94A3B8' }} angle={-18} textAnchor="end" height={50} />
              <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '11px', color: '#64748B' }} />
              <Bar dataKey="complaints" name="Complaints %" fill="#EA5455" radius={[4, 4, 0, 0]} fillOpacity={0.85} />
              <Bar dataKey="praises"    name="Praises %"    fill="#28C76F" radius={[4, 4, 0, 0]} fillOpacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* ── Product Satisfaction Section ── */}
      <ProductSatisfactionSection />

      {/* ── Bot Risk + Recommendation + Orchestrator ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot Risk */}
        {botData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card-3d p-5"
          >
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                style={{ background: '#FEE2E2' }}>
                <Shield size={14} style={{ color: '#DC2626' }} />
              </div>
              <h3 className="font-semibold text-sm" style={{ color: '#1E293B' }}>Bot Risk Breakdown</h3>
            </div>
            <div className="space-y-3">
              {[
                { level: 'critical', color: '#DC2626', bg: '#FEE2E2', label: 'Critical' },
                { level: 'high',     color: '#EA5455', bg: '#FEE2E2', label: 'High' },
                { level: 'medium',   color: '#FFB547', bg: '#FEF3C7', label: 'Medium' },
                { level: 'low',      color: '#28C76F', bg: '#DCFCE7', label: 'Low' },
              ].map(({ level, color, bg, label }) => {
                const count = botData.riskCounts[level] || 0
                const pct   = Math.round((count / Math.max(report.total_reviews, 1)) * 100)
                return (
                  <div key={level}>
                    <div className="flex justify-between text-xs mb-1.5">
                      <span style={{ color: '#475569' }}>{label}</span>
                      <span className="font-semibold" style={{ color }}>{count} ({pct}%)</span>
                    </div>
                    <div className="progress-track">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 0.8 }}
                        className="progress-fill"
                        style={{ background: color }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
            <div className="mt-4 pt-3 border-t flex justify-between text-xs" style={{ borderColor: '#E5E7EB' }}>
              <span style={{ color: '#64748B' }}>Authentic review rate</span>
              <span className="font-bold" style={{ color: '#28C76F' }}>{botData.authenticRate}%</span>
            </div>
          </motion.div>
        )}

        {/* Top Recommendation */}
        {topRec && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
            className="card-3d p-5"
            style={{
              borderColor: topRec.priority === 1 ? '#FECACA' : '#FDE68A',
              background: topRec.priority === 1 ? '#FFF5F5' : '#FFFDF0',
            }}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold"
                style={{
                  background: topRec.priority === 1 ? '#FEE2E2' : '#FEF3C7',
                  color:      topRec.priority === 1 ? '#B91C1C' : '#B45309',
                }}>
                P{topRec.priority} · {topRec.category.toUpperCase()}
              </span>
              <span className="text-xs" style={{ color: '#94A3B8' }}>Top Recommendation</span>
            </div>
            <h4 className="font-semibold text-sm mb-2" style={{ color: '#1E293B' }}>{topRec.title}</h4>
            <p className="text-xs leading-relaxed mb-3" style={{ color: '#475569' }}>{topRec.description}</p>
            <div className="pt-3 border-t" style={{ borderColor: '#E5E7EB' }}>
              <div className="text-xs font-semibold mb-1" style={{ color: '#FF7A00' }}>Suggested Action</div>
              <div className="text-xs" style={{ color: '#64748B' }}>{topRec.suggested_action}</div>
            </div>
          </motion.div>
        )}

        {/* Orchestrator Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card-3d p-5"
        >
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: '#EDE9FE' }}>
              <Brain size={14} style={{ color: '#7C3AED' }} />
            </div>
            <h3 className="font-semibold text-sm" style={{ color: '#1E293B' }}>Orchestrator Summary</h3>
          </div>
          <div className="space-y-3">
            {[
              { label: 'Pipeline Version', val: report.pipeline_version || '2.0', color: '#2563EB' },
              { label: 'Decisions Made',   val: decisions.length,                 color: '#7C3AED' },
              { label: 'Feedback Loops',   val: feedbackLoops,                    color: feedbackLoops > 0 ? '#D97706' : '#28C76F' },
              { label: 'Languages',        val: report.languages_detected?.join(', ') || 'en', color: '#0891B2' },
              { label: 'Categories',       val: report.product_categories?.length || 1, color: '#28C76F' },
            ].map(({ label, val, color }) => (
              <div key={label} className="flex items-center justify-between text-xs">
                <span style={{ color: '#64748B' }}>{label}</span>
                <span className="font-bold font-mono" style={{ color }}>{val}</span>
              </div>
            ))}
          </div>
          {feedbackLoops > 0 && (
            <div className="mt-3 pt-3 border-t flex items-center gap-2 text-xs"
              style={{ borderColor: '#E5E7EB', color: '#D97706' }}>
              <Repeat size={11} />
              Self-corrected via feedback loop
            </div>
          )}
        </motion.div>
      </div>

      {/* ── Agent trace ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.55 }}
        className="card-3d p-6"
      >
        <h3 className="section-header mb-4">Agent Execution Trace</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {agentTrace.map((step, i) => (
            <div key={i}
              className="flex items-center gap-3 rounded-xl p-3"
              style={{ background: '#F8FAFC', border: '1px solid #E5E7EB' }}>
              <div className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{
                  background: step.agent.includes('Orchestrator') ? '#EDE9FE' : '#DCFCE7',
                  border: `1px solid ${step.agent.includes('Orchestrator') ? '#DDD6FE' : '#BBF7D0'}`,
                }}>
                {step.agent.includes('Orchestrator')
                  ? <Brain size={11} style={{ color: '#7C3AED' }} />
                  : <CheckCircle size={11} style={{ color: '#16A34A' }} />}
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-xs font-semibold block truncate" style={{ color: '#1E293B' }}>{step.agent}</span>
                <span className="text-xs block truncate" style={{ color: '#94A3B8' }}>{step.output}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
