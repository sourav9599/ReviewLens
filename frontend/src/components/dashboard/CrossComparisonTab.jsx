import { motion } from 'framer-motion'
import { useReviewStore } from '../../store/reviewStore'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, Cell
} from 'recharts'
import { Trophy, TrendingDown, Globe, Layers } from 'lucide-react'

const CATEGORY_COLORS = [
  '#2563EB', '#7C3AED', '#16A34A', '#D97706', '#DB2777', '#DC2626', '#0891B2'
]

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-3 py-2.5 rounded-xl text-xs border"
      style={{ background: '#FFFFFF', borderColor: '#E5E7EB', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
      {label && <div className="font-semibold mb-1.5" style={{ color: '#1E293B' }}>{label}</div>}
      {payload.map(p => (
        <div key={p.dataKey} className="flex items-center gap-2 mb-0.5">
          <div className="w-2 h-2 rounded-full" style={{ background: p.fill || p.color }} />
          <span style={{ color: '#64748B' }}>{p.name}:</span>
          <span className="font-semibold" style={{ color: '#1E293B' }}>{p.value}%</span>
        </div>
      ))}
    </div>
  )
}

export default function CrossComparisonTab() {
  const { getCrossComparisonData } = useReviewStore()
  const data = getCrossComparisonData()

  if (!data || !data.categories?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
          style={{ background: '#DBEAFE', border: '1px solid #BFDBFE' }}>
          <Layers size={28} style={{ color: '#2563EB' }} />
        </div>
        <h3 className="font-semibold text-lg mb-2" style={{ color: '#1E293B' }}>Cross-Comparison Not Available</h3>
        <p className="text-sm max-w-sm" style={{ color: '#94A3B8' }}>
          Upload reviews with multiple product categories (at least 2) to enable cross-product comparison.
        </p>
      </div>
    )
  }

  const { categories, sentiment_by_category, review_count_by_category,
    best_category, worst_category, bot_rate_by_category } = data

  const sentimentBarData = categories.map((cat, i) => ({
    category: cat.length > 12 ? cat.slice(0, 12) + '…' : cat,
    fullName: cat,
    Positive: Math.round((sentiment_by_category[cat]?.positive || 0) * 100),
    Negative: Math.round((sentiment_by_category[cat]?.negative || 0) * 100),
    Neutral:  Math.round((sentiment_by_category[cat]?.neutral  || 0) * 100),
    color: CATEGORY_COLORS[i % CATEGORY_COLORS.length],
  }))

  const radarData = ['positive', 'negative', 'neutral', 'mixed'].map(metric => {
    const entry = { metric: metric.charAt(0).toUpperCase() + metric.slice(1) }
    categories.forEach(cat => {
      entry[cat] = Math.round((sentiment_by_category[cat]?.[metric] || 0) * 100)
    })
    return entry
  })

  return (
    <div className="space-y-6">
      {/* Best/Worst Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="rounded-2xl p-5 flex items-center gap-4"
          style={{ background: '#F0FDF4', border: '1px solid #86EFAC' }}
        >
          <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: '#DCFCE7', border: '1px solid #BBF7D0' }}>
            <Trophy size={22} style={{ color: '#16A34A' }} />
          </div>
          <div>
            <div className="text-xs font-semibold mb-1" style={{ color: '#16A34A' }}>Best Performing Category</div>
            <div className="font-bold text-xl" style={{ color: '#15803D' }}>
              {best_category || 'N/A'}
            </div>
            <div className="text-xs mt-0.5" style={{ color: '#64748B' }}>
              {Math.round((sentiment_by_category[best_category]?.positive || 0) * 100)}% positive sentiment
              · {review_count_by_category[best_category] || 0} reviews
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="rounded-2xl p-5 flex items-center gap-4"
          style={{ background: '#FEF2F2', border: '1px solid #FCA5A5' }}
        >
          <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: '#FEE2E2', border: '1px solid #FECACA' }}>
            <TrendingDown size={22} style={{ color: '#DC2626' }} />
          </div>
          <div>
            <div className="text-xs font-semibold mb-1" style={{ color: '#DC2626' }}>Needs Most Attention</div>
            <div className="font-bold text-xl" style={{ color: '#B91C1C' }}>
              {worst_category || 'N/A'}
            </div>
            <div className="text-xs mt-0.5" style={{ color: '#64748B' }}>
              {Math.round((sentiment_by_category[worst_category]?.negative || 0) * 100)}% negative sentiment
              · {review_count_by_category[worst_category] || 0} reviews
            </div>
          </div>
        </motion.div>
      </div>

      {/* Category Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {categories.map((cat, i) => {
          const color = CATEGORY_COLORS[i % CATEGORY_COLORS.length]
          const pos = Math.round((sentiment_by_category[cat]?.positive || 0) * 100)
          const neg = Math.round((sentiment_by_category[cat]?.negative || 0) * 100)
          const botRate = Math.round((bot_rate_by_category[cat] || 0) * 100)
          const count = review_count_by_category[cat] || 0
          const isBest = cat === best_category
          const isWorst = cat === worst_category

          return (
            <motion.div
              key={cat}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              className="card-3d p-4"
              style={isBest ? { borderColor: '#86EFAC', background: '#F0FDF4' } : isWorst ? { borderColor: '#FCA5A5', background: '#FEF2F2' } : {}}
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 rounded-lg flex items-center justify-center"
                  style={{ background: `${color}15`, border: `1px solid ${color}40` }}>
                  <Globe size={11} style={{ color }} />
                </div>
                <span className="text-xs font-semibold truncate flex-1" style={{ color: '#1E293B' }}>{cat}</span>
                {isBest && <span className="text-xs">🏆</span>}
                {isWorst && <span className="text-xs">⚠️</span>}
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs mb-1">
                  <span style={{ color: '#64748B' }}>Positive</span>
                  <span className="font-semibold" style={{ color: '#16A34A' }}>{pos}%</span>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pos}%` }}
                    transition={{ duration: 0.8, delay: i * 0.06 }}
                    className="h-full rounded-full"
                    style={{ background: '#28C76F' }}
                  />
                </div>
                <div className="flex justify-between text-xs mb-1">
                  <span style={{ color: '#64748B' }}>Negative</span>
                  <span className="font-semibold" style={{ color: '#DC2626' }}>{neg}%</span>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${neg}%` }}
                    transition={{ duration: 0.8, delay: i * 0.06 + 0.1 }}
                    className="h-full rounded-full"
                    style={{ background: '#EA5455' }}
                  />
                </div>
                <div className="flex justify-between text-xs mt-1 pt-1.5" style={{ borderTop: '1px solid #E5E7EB' }}>
                  <span style={{ color: '#94A3B8' }}>{count} reviews</span>
                  <span className="font-medium" style={{ color: botRate > 20 ? '#DC2626' : '#94A3B8' }}>
                    {botRate}% bots
                  </span>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Sentiment Comparison Bar Chart */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card-3d p-6"
      >
        <h3 className="section-header">Sentiment by Category</h3>
        <p className="section-subtext mb-5">Side-by-side positive / negative comparison across product categories</p>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={sentimentBarData} barSize={14} barGap={3}>
            <XAxis dataKey="category" tick={{ fontSize: 10, fill: '#94A3B8' }} />
            <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: '11px', color: '#64748B' }} />
            <Bar dataKey="Positive" fill="#28C76F" radius={[3, 3, 0, 0]} fillOpacity={0.9} />
            <Bar dataKey="Negative" fill="#EA5455" radius={[3, 3, 0, 0]} fillOpacity={0.9} />
            <Bar dataKey="Neutral"  fill="#94A3B8" radius={[3, 3, 0, 0]} fillOpacity={0.7} />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Radar Chart */}
      {radarData.length > 0 && categories.length >= 2 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card-3d p-6"
        >
          <h3 className="section-header">Sentiment Profile Radar</h3>
          <p className="section-subtext mb-5">Multi-dimensional sentiment comparison per category</p>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#E5E7EB" />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: '#64748B' }} />
              {categories.slice(0, 4).map((cat, i) => (
                <Radar
                  key={cat}
                  name={cat}
                  dataKey={cat}
                  stroke={CATEGORY_COLORS[i]}
                  fill={CATEGORY_COLORS[i]}
                  fillOpacity={0.1}
                  strokeWidth={2}
                />
              ))}
              <Legend wrapperStyle={{ fontSize: '11px', color: '#64748B' }} />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        </motion.div>
      )}
    </div>
  )
}
