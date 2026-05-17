import { motion } from 'framer-motion'
import { Zap, ShoppingBag, Megaphone, Settings, Star } from 'lucide-react'
import { useReviewStore } from '../../store/reviewStore'

const CATEGORY_STYLES = {
  product:    { color: '#2563EB', bg: '#DBEAFE', border: '#BFDBFE', icon: ShoppingBag, label: 'Product' },
  marketing:  { color: '#7C3AED', bg: '#EDE9FE', border: '#DDD6FE', icon: Megaphone,   label: 'Marketing' },
  operations: { color: '#D97706', bg: '#FEF3C7', border: '#FDE68A', icon: Settings,    label: 'Operations' },
  quality:    { color: '#DC2626', bg: '#FEE2E2', border: '#FECACA', icon: Star,         label: 'Quality Control' },
}

const PRIORITY_STYLES = {
  1: { label: 'P1 Critical', color: '#DC2626', bg: '#FEF2F2', border: '#FECACA', badgeBg: '#FEE2E2' },
  2: { label: 'P2 High',     color: '#D97706', bg: '#FFFBEB', border: '#FDE68A', badgeBg: '#FEF3C7' },
  3: { label: 'P3 Medium',   color: '#2563EB', bg: '#EFF6FF', border: '#BFDBFE', badgeBg: '#DBEAFE' },
  4: { label: 'P4 Low',      color: '#64748B', bg: '#F8FAFC', border: '#E2E8F0', badgeBg: '#F1F5F9' },
}

export default function RecommendationsTab() {
  const { report } = useReviewStore()
  if (!report) return null

  const recommendations = report.recommendations || []

  const grouped = { 1: [], 2: [], 3: [], 4: [] }
  recommendations.forEach(r => {
    const p = Math.min(4, Math.max(1, r.priority))
    grouped[p].push(r)
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="font-bold text-2xl" style={{ color: '#1E293B' }}>Actionable Recommendations</h2>
          <p className="text-sm mt-1" style={{ color: '#64748B' }}>
            LLM-generated, data-driven insights for product and marketing teams
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {[1, 2, 3, 4].map(p => {
            const count = grouped[p].length
            if (!count) return null
            const { label, color, bg, border } = PRIORITY_STYLES[p]
            return (
              <div key={p} className="px-3 py-1.5 rounded-xl text-xs font-semibold"
                style={{ background: bg, border: `1px solid ${border}`, color }}>
                {count} {label}
              </div>
            )
          })}
        </div>
      </div>

      {recommendations.length === 0 && (
        <div className="card-3d p-12 text-center">
          <Zap size={40} className="mx-auto mb-4" style={{ color: '#CBD5E1' }} />
          <p style={{ color: '#94A3B8' }}>No recommendations generated yet</p>
        </div>
      )}

      {/* Recommendation cards */}
      <div className="space-y-4">
        {recommendations.map((rec, i) => {
          const p = Math.min(4, Math.max(1, rec.priority))
          const { color: pColor, bg: pBg, border: pBorder, badgeBg, label: pLabel } = PRIORITY_STYLES[p]
          const catStyle = CATEGORY_STYLES[rec.category] || CATEGORY_STYLES.product
          const CatIcon = catStyle.icon

          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="rounded-2xl p-6 border"
              style={{ background: pBg, borderColor: pBorder }}
            >
              <div className="flex items-start gap-5">
                {/* Priority badge */}
                <div className="flex-shrink-0">
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center font-bold font-mono text-sm"
                    style={{ background: badgeBg, border: `1.5px solid ${pBorder}`, color: pColor }}>
                    P{p}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  {/* Header row */}
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    <h3 className="font-semibold text-base" style={{ color: '#1E293B' }}>{rec.title}</h3>
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg text-xs font-medium"
                      style={{ background: catStyle.bg, color: catStyle.color, border: `1px solid ${catStyle.border}` }}>
                      <CatIcon size={10} />
                      {catStyle.label}
                    </div>
                    {rec.affected_feature && (
                      <span className="px-2 py-0.5 rounded-lg text-xs font-mono capitalize"
                        style={{ background: '#F1F5F9', color: '#64748B', border: '1px solid #E2E8F0' }}>
                        #{rec.affected_feature.replace(/_/g, '-')}
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-sm leading-relaxed mb-4" style={{ color: '#475569' }}>
                    {rec.description}
                  </p>

                  {/* 3-col detail grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="rounded-xl p-3.5"
                      style={{ background: '#FFFFFF', border: '1px solid #E5E7EB' }}>
                      <div className="text-xs font-semibold mb-1.5" style={{ color: '#94A3B8' }}>📊 Supporting Data</div>
                      <div className="text-sm" style={{ color: '#475569' }}>{rec.supporting_data}</div>
                    </div>
                    <div className="rounded-xl p-3.5"
                      style={{ background: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                      <div className="text-xs font-semibold mb-1.5" style={{ color: '#2563EB' }}>⚡ Suggested Action</div>
                      <div className="text-sm" style={{ color: '#1E40AF' }}>{rec.suggested_action}</div>
                    </div>
                    <div className="rounded-xl p-3.5"
                      style={{ background: '#F0FDF4', border: '1px solid #BBF7D0' }}>
                      <div className="text-xs font-semibold mb-1.5" style={{ color: '#16A34A' }}>🎯 Estimated Impact</div>
                      <div className="text-sm" style={{ color: '#15803D' }}>{rec.estimated_impact}</div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Category summary */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card-3d p-6"
      >
        <h3 className="section-header mb-4">By Category</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(CATEGORY_STYLES).map(([key, { color, bg, border, icon: Icon, label }]) => {
            const count = recommendations.filter(r => r.category === key).length
            return (
              <div key={key} className="text-center p-4 rounded-2xl"
                style={{ background: bg, border: `1px solid ${border}` }}>
                <Icon size={20} className="mx-auto mb-2" style={{ color }} />
                <div className="text-2xl font-bold" style={{ color }}>{count}</div>
                <div className="text-xs font-semibold mt-1" style={{ color: '#1E293B' }}>{label}</div>
              </div>
            )
          })}
        </div>
      </motion.div>
    </div>
  )
}
