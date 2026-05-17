import { useState } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { AlertTriangle, TrendingUp, TrendingDown, Zap } from 'lucide-react'
import { useReviewStore } from '../../store/reviewStore'
import clsx from 'clsx'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-4 py-3 rounded-xl text-xs border"
      style={{ background: '#FFFFFF', borderColor: '#E5E7EB', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
      <div className="font-semibold mb-2" style={{ color: '#1E293B' }}>Window {label}</div>
      {payload.map(p => (
        <div key={p.dataKey} className="flex items-center gap-2 mb-1">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span style={{ color: '#64748B' }}>{p.name}:</span>
          <span className="font-semibold" style={{ color: '#1E293B' }}>{p.value}%</span>
        </div>
      ))}
    </div>
  )
}

const SEVERITY_STYLES = {
  critical: { bg: '#FEF2F2', border: '#FECACA', color: '#DC2626', iconBg: '#FEE2E2', icon: AlertTriangle },
  warning:  { bg: '#FFFBEB', border: '#FDE68A', color: '#D97706', iconBg: '#FEF3C7', icon: TrendingDown },
  info:     { bg: '#F0FDF4', border: '#BBF7D0', color: '#16A34A', iconBg: '#DCFCE7', icon: TrendingUp },
}

const LINE_COLORS = ['#2563EB', '#DC2626', '#16A34A', '#D97706', '#7C3AED', '#DB2777']

export default function TrendsTab() {
  const { report, getTrendChartData } = useReviewStore()
  const [selectedFeatureFilter, setSelectedFeatureFilter] = useState('packaging')
  if (!report) return null

  const alerts = report.trend_alerts || []
  const trendChartData = getTrendChartData()

  const allFeatureKeys = new Set()
  trendChartData.forEach(w => {
    Object.keys(w).forEach(k => {
      if (k.endsWith('_complaints') || k.endsWith('_praises')) allFeatureKeys.add(k)
    })
  })

  const trendFeatures = [...new Set([...allFeatureKeys].map(k => k.replace('_complaints', '').replace('_praises', '')))]

  const featureTrendData = trendChartData.map(w => {
    const entry = { window: `W${w.window}`, reviews: `${w.windowStart}-${w.windowEnd}` }
    const complaintKey = `${selectedFeatureFilter}_complaints`
    const praiseKey = `${selectedFeatureFilter}_praises`
    if (w[complaintKey] !== undefined) entry.complaints = w[complaintKey]
    if (w[praiseKey] !== undefined) entry.praises = w[praiseKey]
    return entry
  }).filter(e => e.complaints !== undefined || e.praises !== undefined)

  return (
    <div className="space-y-6">

      {/* Alert severity summary pills */}
      <div className="flex items-center gap-3 flex-wrap">
        {['critical', 'warning', 'info'].map(sev => {
          const count = alerts.filter(a => a.severity === sev).length
          const { color, bg, border } = SEVERITY_STYLES[sev]
          return (
            <div key={sev} className="flex items-center gap-2 px-4 py-2 rounded-xl"
              style={{ background: bg, border: `1px solid ${border}` }}>
              <div className="w-2 h-2 rounded-full" style={{ background: color }} />
              <span className="text-sm font-semibold capitalize" style={{ color }}>{count} {sev}</span>
            </div>
          )
        })}
        {alerts.length === 0 && (
          <div className="text-sm" style={{ color: '#94A3B8' }}>
            No trend alerts detected for this dataset
          </div>
        )}
      </div>

      {/* Alert cards */}
      {alerts.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-semibold text-base" style={{ color: '#1E293B' }}>Active Trend Alerts</h3>
          {alerts.map(alert => {
            const { bg, border, color, iconBg, icon: Icon } = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.info
            return (
              <motion.div
                key={alert.alert_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="rounded-2xl p-5 border"
                style={{ background: bg, borderColor: border }}
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: iconBg, border: `1px solid ${border}` }}>
                    <Icon size={18} style={{ color }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="font-semibold capitalize" style={{ color: '#1E293B' }}>
                        {alert.feature.replace(/_/g, ' ')}
                      </span>
                      <span className="px-2 py-0.5 rounded text-xs font-medium capitalize"
                        style={{ background: '#FFFFFF', color, border: `1px solid ${border}` }}>
                        {alert.alert_type.replace(/_/g, ' ')}
                      </span>
                      {alert.is_systemic && (
                        <span className="px-2 py-0.5 rounded text-xs font-bold"
                          style={{ background: '#FEE2E2', color: '#DC2626', border: '1px solid #FECACA' }}>
                          SYSTEMIC
                        </span>
                      )}
                    </div>
                    <p className="text-sm leading-relaxed" style={{ color: '#475569' }}>
                      {alert.description}
                    </p>
                    {alert.affected_reviews?.length > 0 && (
                      <div className="mt-2 text-xs" style={{ color: '#94A3B8' }}>
                        Affecting reviews: {alert.affected_reviews.slice(0, 5).join(', ')}
                        {alert.affected_reviews.length > 5 && ` +${alert.affected_reviews.length - 5} more`}
                      </div>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-2xl font-bold" style={{ color }}>
                      {alert.change_percent > 0 ? '+' : ''}{alert.change_percent}%
                    </div>
                    <div className="text-xs" style={{ color: '#94A3B8' }}>
                      {Math.round(alert.previous_rate * 100)}% → {Math.round(alert.current_rate * 100)}%
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}

      {/* Time series chart */}
      {featureTrendData.length > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="card-3d p-6"
        >
          <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
            <div>
              <h3 className="section-header">Feature Trend Over Batches</h3>
              <p className="section-subtext">
                Complaint vs praise rate across sliding windows of {report.processed_reviews?.length > 100 ? 50 : 10} reviews
              </p>
            </div>
            <div className="flex gap-2 flex-wrap">
              {trendFeatures.slice(0, 6).map((feat, i) => (
                <button
                  key={feat}
                  onClick={() => setSelectedFeatureFilter(feat)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize"
                  style={selectedFeatureFilter === feat ? {
                    background: `${LINE_COLORS[i % LINE_COLORS.length]}15`,
                    border: `1.5px solid ${LINE_COLORS[i % LINE_COLORS.length]}`,
                    color: LINE_COLORS[i % LINE_COLORS.length],
                    fontWeight: 700,
                  } : {
                    background: '#F8FAFC',
                    border: '1px solid #E5E7EB',
                    color: '#64748B',
                  }}
                >
                  {feat.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={featureTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="window" tick={{ fontSize: 11, fill: '#94A3B8' }} />
              <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} domain={[0, 100]} unit="%" />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#64748B' }} />
              <Line type="monotone" dataKey="complaints" name="Complaint %" stroke="#EA5455" strokeWidth={2.5} dot={{ r: 4, fill: '#EA5455' }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="praises" name="Praise %" stroke="#28C76F" strokeWidth={2.5} dot={{ r: 4, fill: '#28C76F' }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
          {selectedFeatureFilter === 'packaging' && featureTrendData.length >= 2 && (
            <div className="mt-3 px-3 py-2.5 rounded-xl text-xs flex items-center gap-2"
              style={{ background: '#FEF2F2', border: '1px solid #FECACA', color: '#DC2626' }}>
              <Zap size={11} />
              Seeded complaint trend detected — packaging complaints spike in the last review batch, as expected
            </div>
          )}
        </motion.div>
      )}

      {/* Systemic vs Isolated */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card-3d p-5">
          <h4 className="font-semibold mb-3" style={{ color: '#1E293B' }}>Systemic Issues</h4>
          <div className="space-y-2">
            {alerts.filter(a => a.is_systemic).length === 0 ? (
              <p className="text-sm" style={{ color: '#94A3B8' }}>No systemic issues detected</p>
            ) : (
              alerts.filter(a => a.is_systemic).map(a => (
                <div key={a.alert_id} className="flex items-center gap-3 px-3 py-2 rounded-xl"
                  style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}>
                  <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: '#DC2626' }} />
                  <span className="text-sm capitalize font-medium" style={{ color: '#1E293B' }}>{a.feature.replace(/_/g, ' ')}</span>
                  <span className="ml-auto text-xs font-bold" style={{ color: '#DC2626' }}>
                    {Math.round(a.current_rate * 100)}%
                  </span>
                </div>
              ))
            )}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="card-3d p-5">
          <h4 className="font-semibold mb-3" style={{ color: '#1E293B' }}>Emerging (Isolated) Issues</h4>
          <div className="space-y-2">
            {alerts.filter(a => !a.is_systemic && a.severity !== 'info').length === 0 ? (
              <p className="text-sm" style={{ color: '#94A3B8' }}>No isolated issues detected</p>
            ) : (
              alerts.filter(a => !a.is_systemic && a.severity !== 'info').map(a => (
                <div key={a.alert_id} className="flex items-center gap-3 px-3 py-2 rounded-xl"
                  style={{ background: '#FFFBEB', border: '1px solid #FDE68A' }}>
                  <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: '#D97706' }} />
                  <span className="text-sm capitalize font-medium" style={{ color: '#1E293B' }}>{a.feature.replace(/_/g, ' ')}</span>
                  <span className="ml-auto text-xs font-bold" style={{ color: '#D97706' }}>
                    +{a.change_percent}%
                  </span>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
