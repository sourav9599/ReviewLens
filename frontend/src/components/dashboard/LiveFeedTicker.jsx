import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Radio, ChevronRight, X, Wifi } from 'lucide-react'
import { useReviewStore } from '../../store/reviewStore'

const SENTIMENT_CONFIG = {
  positive:  { label: 'Positive',   emoji: '😊', badgeClass: 'badge-positive',  dot: '#28C76F' },
  negative:  { label: 'Negative',   emoji: '😠', badgeClass: 'badge-negative',  dot: '#EA5455' },
  neutral:   { label: 'Neutral',    emoji: '😐', badgeClass: 'badge-neutral',   dot: '#FFB547' },
  mixed:     { label: 'Mixed',      emoji: '🔀', badgeClass: 'badge-mixed',     dot: '#F7936F' },
  sarcastic: { label: 'Sarcastic',  emoji: '😏', badgeClass: 'badge-sarcastic', dot: '#A78BFA' },
  ambiguous: { label: 'Ambiguous',  emoji: '❓', badgeClass: 'badge-ambiguous', dot: '#60A5FA' },
}

function ReviewCard({ review, onClose }) {
  const cfg = SENTIMENT_CONFIG[review.overall_sentiment] || SENTIMENT_CONFIG.neutral
  return (
    <motion.div
      layout
      initial={{ x: 340, opacity: 0, scale: 0.94 }}
      animate={{ x: 0,   opacity: 1, scale: 1 }}
      exit={{    x: -340, opacity: 0, scale: 0.94 }}
      transition={{ type: 'spring', stiffness: 280, damping: 26 }}
      className="relative rounded-2xl p-4 border"
      style={{
        background: '#FFFFFF',
        borderColor: '#E5E7EB',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04)',
      }}
    >
      {/* Live indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5">
        <span className="live-dot w-2 h-2 rounded-full" style={{ background: cfg.dot }} />
        <span className="text-xs font-medium" style={{ color: '#94A3B8' }}>LIVE</span>
      </div>

      <div className="flex items-start gap-3 pr-8">
        <div className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center text-lg"
          style={{ background: '#F8FAFC', border: '1px solid #E5E7EB' }}>
          {cfg.emoji}
        </div>
        <div className="flex-1 min-w-0">
          {/* Product + badge row */}
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="text-xs font-semibold truncate" style={{ color: '#1E293B', maxWidth: 140 }}>
              {review.product_name || 'Product'}
            </span>
            <span className={`sentiment-badge ${cfg.badgeClass}`}>
              {cfg.label}
            </span>
            {review.rating && (
              <span className="text-xs font-semibold" style={{ color: '#FFB547' }}>★ {review.rating}</span>
            )}
          </div>
          {/* Review text */}
          <p className="text-xs leading-relaxed line-clamp-2" style={{ color: '#475569' }}>
            "{review.cleaned_text?.slice(0, 130)}{review.cleaned_text?.length > 130 ? '…' : ''}"
          </p>
          {/* Feature tags */}
          {review.feature_sentiments?.length > 0 && (
            <div className="flex gap-1 mt-2 flex-wrap">
              {review.feature_sentiments.slice(0, 3).map(fs => {
                const fCfg = SENTIMENT_CONFIG[fs.sentiment] || SENTIMENT_CONFIG.neutral
                return (
                  <span key={fs.feature}
                    className="text-xs px-1.5 py-0.5 rounded-full font-medium"
                    style={{ background: '#F1F5F9', color: '#64748B' }}>
                    {fs.feature}
                  </span>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default function LiveFeedTicker({ isOpen, onToggle }) {
  const { getLiveFeedReviews } = useReviewStore()
  const [feedReviews, setFeedReviews] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [visible, setVisible] = useState([])
  const intervalRef = useRef(null)
  const allReviews = useRef([])

  useEffect(() => {
    allReviews.current = getLiveFeedReviews()
    if (allReviews.current.length > 0) {
      setVisible([allReviews.current[0]])
    }
  }, [])

  useEffect(() => {
    if (!isOpen) {
      clearInterval(intervalRef.current)
      return
    }

    const reviews = allReviews.current
    if (!reviews.length) return

    // Show first immediately
    setVisible([reviews[0]])
    let idx = 1

    intervalRef.current = setInterval(() => {
      const next = reviews[idx % reviews.length]
      setVisible([next])
      idx++
    }, 3500)

    return () => clearInterval(intervalRef.current)
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 pointer-events-none flex items-end justify-end">
      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 40, scale: 0.95 }}
        transition={{ type: 'spring', stiffness: 320, damping: 30 }}
        className="pointer-events-auto m-6 w-96 rounded-2xl border overflow-hidden"
        style={{
          background: '#F8FAFC',
          borderColor: '#E5E7EB',
          boxShadow: '0 20px 60px rgba(0,0,0,0.14), 0 6px 20px rgba(0,0,0,0.07)',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b"
          style={{ borderColor: '#E5E7EB', background: '#FFFFFF' }}>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ background: '#FFF3E8', border: '1px solid #FED7AA' }}>
              <Radio size={13} style={{ color: '#FF7A00' }} />
            </div>
            <div>
              <div className="text-sm font-semibold" style={{ color: '#1E293B' }}>Live Review Feed</div>
              <div className="text-xs flex items-center gap-1.5" style={{ color: '#94A3B8' }}>
                <span className="live-dot w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                Simulated real-time stream
              </div>
            </div>
          </div>
          <button onClick={onToggle}
            className="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
            style={{ background: '#F1F5F9', color: '#64748B' }}
            onMouseEnter={e => e.currentTarget.style.background = '#E2E8F0'}
            onMouseLeave={e => e.currentTarget.style.background = '#F1F5F9'}>
            <X size={14} />
          </button>
        </div>

        {/* Feed area */}
        <div className="p-4 min-h-40 relative">
          <AnimatePresence mode="popLayout">
            {visible.map((review, i) => (
              <ReviewCard
                key={`${review.id}-${i}`}
                review={review}
                onClose={() => setVisible([])}
              />
            ))}
          </AnimatePresence>

          {visible.length === 0 && (
            <div className="flex items-center justify-center h-32 text-sm" style={{ color: '#94A3B8' }}>
              Waiting for reviews…
            </div>
          )}
        </div>

        {/* Sentiment legend */}
        <div className="px-4 pb-3 flex flex-wrap gap-x-3 gap-y-1.5">
          {Object.entries(SENTIMENT_CONFIG).map(([key, cfg]) => (
            <div key={key} className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: cfg.dot }} />
              <span className="text-xs" style={{ color: '#94A3B8' }}>{cfg.label}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
