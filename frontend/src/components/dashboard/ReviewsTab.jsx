import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, Globe, Smile, AlertTriangle, Star } from 'lucide-react'
import { useReviewStore } from '../../store/reviewStore'

/* ── Sentiment config ─────────────────────────────────────────────────── */
const SENTIMENT_CONFIG = {
  positive:  { label: 'Positive',  color: '#28C76F', bg: '#DCFCE7', border: '#BBF7D0', emoji: '😊' },
  negative:  { label: 'Negative',  color: '#EA5455', bg: '#FEE2E2', border: '#FECACA', emoji: '😠' },
  neutral:   { label: 'Neutral',   color: '#FFB547', bg: '#FEF3C7', border: '#FDE68A', emoji: '😐' },
  mixed:     { label: 'Mixed',     color: '#F7936F', bg: '#FFF1E6', border: '#FED7AA', emoji: '🔀' },
  sarcastic: { label: 'Sarcastic', color: '#A78BFA', bg: '#EDE9FE', border: '#DDD6FE', emoji: '😏' },
  ambiguous: { label: 'Ambiguous', color: '#60A5FA', bg: '#DBEAFE', border: '#BFDBFE', emoji: '❓' },
}

const STATUS_STYLES = {
  clean:         { color: '#28C76F', bg: '#DCFCE7', border: '#BBF7D0', label: 'Clean' },
  duplicate:     { color: '#94A3B8', bg: '#F1F5F9', border: '#E2E8F0', label: 'Duplicate' },
  near_duplicate:{ color: '#94A3B8', bg: '#F1F5F9', border: '#E2E8F0', label: 'Near-Dup' },
  bot_suspected: { color: '#EA5455', bg: '#FEE2E2', border: '#FECACA', label: 'Bot?' },
  flagged:       { color: '#FFB547', bg: '#FEF3C7', border: '#FDE68A', label: 'Flagged' },
}

const BOT_RISK_STYLES = {
  low:      { color: '#28C76F', label: '✓ Low Risk' },
  medium:   { color: '#FFB547', label: '⚠ Medium Risk' },
  high:     { color: '#EA5455', label: '🚨 High Risk' },
  critical: { color: '#DC2626', label: '☠ Critical' },
}

const ConfidenceBar = ({ score }) => (
  <div className="flex items-center gap-1.5">
    <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
      <div className="h-full rounded-full transition-all"
        style={{
          width: `${Math.round(score * 100)}%`,
          background: score >= 0.8 ? '#28C76F' : score >= 0.5 ? '#FFB547' : '#EA5455',
        }}
      />
    </div>
    <span className="text-xs font-mono" style={{ color: '#94A3B8' }}>
      {Math.round(score * 100)}%
    </span>
  </div>
)

export default function ReviewsTab() {
  const { report } = useReviewStore()
  const [search, setSearch]               = useState('')
  const [filterStatus, setFilterStatus]   = useState('all')
  const [filterSentiment, setFilterSentiment] = useState('all')
  const [filterCategory, setFilterCategory]   = useState('all')
  const [page, setPage]   = useState(0)
  const PAGE_SIZE = 20

  if (!report) return null

  const reviews    = report.processed_reviews || []
  const categories = ['all', ...new Set(reviews.map(r => r.product_category).filter(Boolean))]

  const filtered = useMemo(() => {
    return reviews.filter(r => {
      if (filterStatus    !== 'all' && r.status            !== filterStatus)    return false
      if (filterSentiment !== 'all' && r.overall_sentiment !== filterSentiment) return false
      if (filterCategory  !== 'all' && r.product_category  !== filterCategory)  return false
      if (search) {
        const q = search.toLowerCase()
        if (!r.cleaned_text?.toLowerCase().includes(q) && !r.product_name?.toLowerCase().includes(q)) return false
      }
      return true
    })
  }, [reviews, filterStatus, filterSentiment, filterCategory, search])

  const paged      = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)

  // Sentiment counts for filter badges
  const sentCounts = useMemo(() => {
    const c = {}
    reviews.forEach(r => { c[r.overall_sentiment] = (c[r.overall_sentiment] || 0) + 1 })
    return c
  }, [reviews])

  return (
    <div className="space-y-5">
      {/* ── Filters ── */}
      <div className="card-3d p-4">
        <div className="flex flex-wrap gap-3 items-center">
          {/* Search */}
          <div className="relative flex-1 min-w-48">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#94A3B8' }} />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(0) }}
              placeholder="Search reviews or products…"
              className="w-full rounded-xl pl-9 pr-4 py-2.5 text-sm outline-none transition-all"
              style={{
                background: '#F8FAFC',
                border: '1px solid #E5E7EB',
                color: '#1E293B',
              }}
              onFocus={e => { e.target.style.borderColor = '#FF7A00'; e.target.style.boxShadow = '0 0 0 3px rgba(255,122,0,0.1)' }}
              onBlur={e  => { e.target.style.borderColor = '#E5E7EB'; e.target.style.boxShadow = 'none' }}
            />
          </div>

          {/* Status filter */}
          <select
            value={filterStatus}
            onChange={e => { setFilterStatus(e.target.value); setPage(0) }}
            className="rounded-xl px-3 py-2.5 text-sm outline-none"
            style={{ background: '#F8FAFC', border: '1px solid #E5E7EB', color: '#475569' }}
          >
            {['all', 'clean', 'duplicate', 'near_duplicate', 'bot_suspected'].map(o => (
              <option key={o} value={o}>{o === 'all' ? 'All Status' : STATUS_STYLES[o]?.label || o}</option>
            ))}
          </select>

          {/* Category filter */}
          <select
            value={filterCategory}
            onChange={e => { setFilterCategory(e.target.value); setPage(0) }}
            className="rounded-xl px-3 py-2.5 text-sm outline-none"
            style={{ background: '#F8FAFC', border: '1px solid #E5E7EB', color: '#475569' }}
          >
            {categories.map(c => (
              <option key={c} value={c}>{c === 'all' ? 'All Categories' : c}</option>
            ))}
          </select>

          <span className="text-sm font-medium ml-auto" style={{ color: '#64748B' }}>
            {filtered.length} <span style={{ color: '#94A3B8' }}>of {reviews.length}</span>
          </span>
        </div>

        {/* ── Sentiment filter pill buttons ── */}
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            onClick={() => { setFilterSentiment('all'); setPage(0) }}
            className="px-3 py-1 rounded-full text-xs font-semibold transition-all"
            style={{
              background: filterSentiment === 'all' ? '#FF7A00' : '#F1F5F9',
              color:      filterSentiment === 'all' ? '#FFFFFF'  : '#64748B',
              border:     filterSentiment === 'all' ? 'none'     : '1px solid #E5E7EB',
            }}
          >
            All
          </button>
          {Object.entries(SENTIMENT_CONFIG).map(([key, cfg]) => (
            <button
              key={key}
              onClick={() => { setFilterSentiment(filterSentiment === key ? 'all' : key); setPage(0) }}
              className="px-3 py-1 rounded-full text-xs font-semibold transition-all"
              style={{
                background: filterSentiment === key ? cfg.color : cfg.bg,
                color:      filterSentiment === key ? '#FFFFFF'  : cfg.color,
                border:     `1px solid ${filterSentiment === key ? cfg.color : cfg.border}`,
              }}
            >
              {cfg.emoji} {cfg.label} {sentCounts[key] ? `(${sentCounts[key]})` : ''}
            </button>
          ))}
        </div>
      </div>

      {/* ── Reviews list ── */}
      <div className="space-y-3">
        {paged.map((review, i) => {
          const statusStyle = STATUS_STYLES[review.status] || STATUS_STYLES.clean
          const sentCfg     = SENTIMENT_CONFIG[review.overall_sentiment] || SENTIMENT_CONFIG.neutral

          return (
            <motion.div
              key={review.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.02 }}
              className="card-3d-sm p-5"
            >
              <div className="flex items-start gap-4">
                {/* Sentiment emoji avatar */}
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
                  style={{ background: sentCfg.bg, border: `1px solid ${sentCfg.border}` }}>
                  {sentCfg.emoji}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Header row */}
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    {/* Status badge */}
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                      style={{ background: statusStyle.bg, color: statusStyle.color, border: `1px solid ${statusStyle.border}` }}>
                      {statusStyle.label}
                    </span>
                    {/* Sentiment badge */}
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold capitalize"
                      style={{ background: sentCfg.bg, color: sentCfg.color, border: `1px solid ${sentCfg.border}` }}>
                      {sentCfg.emoji} {review.overall_sentiment}
                    </span>
                    {/* Product */}
                    <span className="text-xs font-medium" style={{ color: '#475569' }}>{review.product_name}</span>
                    {/* Category */}
                    {review.product_category && review.product_category !== 'Unknown' && (
                      <span className="px-2 py-0.5 rounded-full text-xs"
                        style={{ background: '#EDE9FE', color: '#7C3AED', border: '1px solid #DDD6FE' }}>
                        {review.product_category}
                      </span>
                    )}
                    {/* Rating */}
                    {review.rating && (
                      <span className="flex items-center gap-0.5 text-xs font-bold"
                        style={{ color: '#D97706' }}>
                        <Star size={10} fill="#D97706" strokeWidth={0} /> {review.rating}
                      </span>
                    )}
                    {/* Language */}
                    {review.flags?.includes('multilingual') && (
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs"
                        style={{ background: '#ECFEFF', color: '#0891B2', border: '1px solid #A5F3FC' }}>
                        <Globe size={9} /> {review.detected_languages?.join(', ')}
                      </span>
                    )}
                    {/* Date */}
                    {review.review_date && (
                      <span className="text-xs ml-auto" style={{ color: '#94A3B8' }}>{review.review_date}</span>
                    )}
                  </div>

                  {/* Review text */}
                  <p className="text-sm leading-relaxed mb-2.5" style={{ color: '#475569' }}>
                    {review.cleaned_text?.slice(0, 200)}
                    {review.cleaned_text?.length > 200 ? '…' : ''}
                  </p>

                  {/* Bot signals */}
                  {review.bot_signals?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2.5">
                      {review.bot_signals.map(sig => (
                        <span key={sig} className="text-xs px-2 py-0.5 rounded-full"
                          style={{ background: '#FEE2E2', color: '#DC2626', border: '1px solid #FECACA' }}>
                          <AlertTriangle size={9} className="inline mr-1" />{sig.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Bottom row - confidence + feature tags */}
                  <div className="flex items-center gap-3 flex-wrap">
                    <ConfidenceBar score={review.overall_confidence || 0} />

                    {review.feature_sentiments?.slice(0, 4).map(fs => {
                      const fc = SENTIMENT_CONFIG[fs.sentiment] || SENTIMENT_CONFIG.neutral
                      return (
                        <span key={fs.feature}
                          className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                          style={{ background: fc.bg, color: fc.color, border: `1px solid ${fc.border}` }}>
                          {fs.feature}: {fs.sentiment}
                        </span>
                      )
                    })}

                    {review.feature_sentiments?.length > 4 && (
                      <span className="text-xs" style={{ color: '#94A3B8' }}>
                        +{review.feature_sentiments.length - 4} more
                      </span>
                    )}

                    {/* Bot risk */}
                    {review.bot_risk_level && review.bot_risk_level !== 'low' && (
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full"
                        style={{ background: '#FEE2E2', color: BOT_RISK_STYLES[review.bot_risk_level]?.color }}>
                        {BOT_RISK_STYLES[review.bot_risk_level]?.label}
                      </span>
                    )}

                    {/* Emoji signals */}
                    {review.emoji_signals?.length > 0 && (
                      <span className="flex items-center gap-1 ml-auto text-sm">
                        <Smile size={12} style={{ color: '#D97706' }} />
                        {review.emoji_signals.map(s => s.emoji).join('')}
                      </span>
                    )}
                  </div>

                  {/* Review ID + dup info */}
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs font-mono" style={{ color: '#CBD5E1' }}>#{review.id}</span>
                    {review.duplicate_of && (
                      <span className="text-xs font-mono" style={{ color: '#94A3B8' }}>
                        dup of #{review.duplicate_of}
                      </span>
                    )}
                    {review.status === 'bot_suspected' && (
                      <span className="text-xs font-mono" style={{ color: '#EA5455' }}>
                        bot score: {Math.round((review.bot_score || 0) * 100)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}

        {paged.length === 0 && (
          <div className="card-3d p-12 text-center">
            <div className="text-4xl mb-3">🔍</div>
            <div className="text-sm font-medium" style={{ color: '#64748B' }}>No reviews match your filters</div>
          </div>
        )}
      </div>

      {/* ── Pagination ── */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="btn-ghost disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ← Prev
          </button>
          <span className="text-sm" style={{ color: '#64748B' }}>
            Page <span className="font-semibold" style={{ color: '#1E293B' }}>{page + 1}</span> of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="btn-ghost disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
