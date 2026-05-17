import { motion } from 'framer-motion'
import { useReviewStore } from '../../store/reviewStore'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from 'recharts'
import { Smile, TrendingUp, Zap, Heart } from 'lucide-react'

const SENTIMENT_COLORS = {
  positive: '#28C76F',
  negative: '#EA5455',
  neutral:  '#94A3B8',
}

const SENTIMENT_BG = {
  positive: '#DCFCE7',
  negative: '#FEE2E2',
  neutral:  '#F1F5F9',
}

const SENTIMENT_BORDER = {
  positive: '#BBF7D0',
  negative: '#FECACA',
  neutral:  '#E2E8F0',
}

function EmojiBar({ emoji, count, sentiment, maxCount }) {
  const pct = (count / maxCount) * 100
  const color = SENTIMENT_COLORS[sentiment] || '#94A3B8'
  const bg    = SENTIMENT_BG[sentiment]    || '#F1F5F9'

  return (
    <div className="flex items-center gap-3 group">
      <span className="text-2xl w-8 text-center flex-shrink-0">{emoji}</span>
      <div className="flex-1 relative h-7 rounded-xl overflow-hidden"
        style={{ background: '#F1F5F9' }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: Math.random() * 0.3 }}
          className="h-full rounded-xl"
          style={{ background: bg }}
        />
        <div className="absolute inset-0 flex items-center px-2.5">
          <span className="text-xs font-semibold" style={{ color }}>{count}</span>
        </div>
      </div>
      <span className="text-xs font-medium w-20 flex-shrink-0 capitalize"
        style={{ color }}>{sentiment}</span>
    </div>
  )
}

const PieTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="px-3 py-2 rounded-xl text-xs border"
      style={{ background: '#FFFFFF', borderColor: '#E5E7EB', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
      <div className="font-semibold capitalize" style={{ color: '#1E293B' }}>{payload[0].name}</div>
      <div className="font-bold text-lg" style={{ color: payload[0].payload.color }}>{payload[0].value}%</div>
    </div>
  )
}

export default function EmojiAnalysisTab() {
  const { getEmojiData } = useReviewStore()
  const emojiData = getEmojiData()

  if (!emojiData) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="text-5xl mb-4">😶</div>
        <h3 className="font-semibold text-lg mb-2" style={{ color: '#1E293B' }}>No Emoji Data</h3>
        <p className="text-sm" style={{ color: '#94A3B8' }}>
          No emojis were detected in the uploaded reviews.
        </p>
      </div>
    )
  }

  const { topEmojis, total_emojis_found, unique_emojis, reviews_with_emojis,
    emoji_confidence_boosts_applied, emoji_sentiment_distribution,
    top_positive_emojis, top_negative_emojis } = emojiData

  const maxCount = topEmojis[0]?.count || 1

  const sentimentPieData = Object.entries(emoji_sentiment_distribution || {})
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({
      name,
      value: Math.round(value * 100),
      color: SENTIMENT_COLORS[name] || '#94A3B8',
    }))

  const statCards = [
    { icon: Smile,      label: 'Total Emojis',          val: total_emojis_found,               color: '#D97706', bg: '#FEF3C7', border: '#FDE68A', sub: 'across all reviews' },
    { icon: TrendingUp, label: 'Unique Emojis',          val: unique_emojis,                    color: '#2563EB', bg: '#DBEAFE', border: '#BFDBFE', sub: 'distinct signals' },
    { icon: Heart,      label: 'Reviews with Emojis',   val: reviews_with_emojis,              color: '#DB2777', bg: '#FCE7F3', border: '#FBCFE8', sub: 'emoji-rich reviews' },
    { icon: Zap,        label: 'Confidence Boosts',      val: emoji_confidence_boosts_applied,  color: '#16A34A', bg: '#DCFCE7', border: '#BBF7D0', sub: 'applied to sentiment' },
  ]

  return (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ icon: Icon, label, val, color, bg, border, sub }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className="rounded-2xl p-5"
            style={{ background: bg, border: `1px solid ${border}` }}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: '#FFFFFF', border: `1px solid ${border}` }}>
                <Icon size={15} style={{ color }} />
              </div>
            </div>
            <div className="font-bold text-3xl" style={{ color, fontFamily: 'DM Sans, sans-serif' }}>{val}</div>
            <div className="text-xs font-semibold mt-1" style={{ color: '#1E293B' }}>{label}</div>
            <div className="text-xs mt-0.5" style={{ color: '#64748B' }}>{sub}</div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Emojis Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="card-3d p-6 lg:col-span-2"
        >
          <h3 className="section-header">Top Emojis by Frequency</h3>
          <p className="section-subtext mb-5">
            Emoji signals mapped to sentiment — used to boost confidence scores
          </p>
          <div className="space-y-2.5">
            {topEmojis.slice(0, 12).map((item) => (
              <EmojiBar
                key={item.emoji}
                emoji={item.emoji}
                count={item.count}
                sentiment={item.sentiment}
                maxCount={maxCount}
              />
            ))}
            {topEmojis.length === 0 && (
              <p className="text-sm text-center py-6" style={{ color: '#94A3B8' }}>
                No emojis found in reviews
              </p>
            )}
          </div>
        </motion.div>

        {/* Emoji Sentiment Pie */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.25 }}
          className="card-3d p-6"
        >
          <h3 className="section-header">Emoji Sentiment Split</h3>
          <p className="section-subtext mb-4">Distribution of emoji emotional signals</p>

          {sentimentPieData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie
                    data={sentimentPieData}
                    cx="50%" cy="50%"
                    innerRadius={45} outerRadius={70}
                    paddingAngle={3} dataKey="value"
                    stroke="none"
                  >
                    {sentimentPieData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<PieTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-col gap-2 mt-3">
                {sentimentPieData.map(d => (
                  <div key={d.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                      <span className="text-xs capitalize font-medium" style={{ color: '#475569' }}>{d.name}</span>
                    </div>
                    <span className="text-sm font-bold" style={{ color: d.color }}>{d.value}%</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-10 text-sm" style={{ color: '#94A3B8' }}>
              No emoji sentiment data
            </div>
          )}
        </motion.div>
      </div>

      {/* Positive vs Negative Highlight */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl p-5"
          style={{ background: '#F0FDF4', border: '1px solid #BBF7D0' }}
        >
          <h4 className="font-semibold mb-3 text-base" style={{ color: '#15803D' }}>
            😊 Top Positive Emojis
          </h4>
          {top_positive_emojis.length > 0 ? (
            <div className="flex flex-wrap gap-3">
              {top_positive_emojis.map(e => (
                <span key={e} className="text-3xl hover:scale-125 transition-transform cursor-default" title="Positive signal">{e}</span>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: '#94A3B8' }}>No positive emojis detected</p>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.38 }}
          className="rounded-2xl p-5"
          style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}
        >
          <h4 className="font-semibold mb-3 text-base" style={{ color: '#DC2626' }}>
            😡 Top Negative Emojis
          </h4>
          {top_negative_emojis.length > 0 ? (
            <div className="flex flex-wrap gap-3">
              {top_negative_emojis.map(e => (
                <span key={e} className="text-3xl hover:scale-125 transition-transform cursor-default" title="Negative signal">{e}</span>
              ))}
            </div>
          ) : (
            <p className="text-sm" style={{ color: '#94A3B8' }}>No negative emojis detected</p>
          )}
        </motion.div>
      </div>

      {/* Confidence Boost Explainer */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card-3d p-5"
        style={{ borderColor: '#BFDBFE' }}
      >
        <h4 className="font-semibold mb-2 text-sm" style={{ color: '#1E293B' }}>How Emoji Confidence Boosting Works</h4>
        <p className="text-sm leading-relaxed" style={{ color: '#475569' }}>
          When a review contains emojis that <strong style={{ color: '#16A34A' }}>align with</strong> its text sentiment
          (e.g., 😍 in a positive review), the sentiment confidence score is boosted by up to +0.20.
          When emojis <strong style={{ color: '#DC2626' }}>conflict</strong> with text sentiment
          (e.g., 😡 in text labeled as positive), a penalty is applied.
          This makes the overall confidence score more accurate and data-driven.
        </p>
      </motion.div>
    </div>
  )
}
