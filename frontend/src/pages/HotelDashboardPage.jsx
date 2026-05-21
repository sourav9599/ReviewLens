import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3, TrendingUp, Zap, MessageSquare, Star,
  Loader2, Search, ThumbsUp, ThumbsDown,
  AlertTriangle, CheckCircle
} from 'lucide-react'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, RadarChart, PolarGrid,
  PolarAngleAxis, Radar
} from 'recharts'
import { useHotelStore } from '../store/hotelStore'
import clsx from 'clsx'

const TABS = [
  { id: 'overview', label: 'Overview', icon: BarChart3 },
  { id: 'sentiment', label: 'Sentiment', icon: TrendingUp },
  { id: 'categories', label: 'Categories', icon: Star },
  { id: 'reviews', label: 'All Reviews', icon: MessageSquare },
  { id: 'insights', label: 'Insights', icon: Zap },
]

const SENTIMENT_COLORS = {
  positive: '#28C76F',
  negative: '#EA5455',
  neutral: '#FFB547',
  mixed: '#F7936F',
}

const SENTIMENT_BG = {
  positive: '#DCFCE7',
  negative: '#FEE2E2',
  neutral: '#FEF3C7',
  mixed: '#FFF1E6',
}

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="px-3 py-2 rounded-lg text-xs border bg-white shadow-lg" style={{ borderColor: '#E5E7EB' }}>
      {payload.map(p => (
        <div key={p.name || p.dataKey} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color || p.fill }} />
          <span className="text-gray-500">{p.name || p.dataKey}:</span>
          <span className="font-semibold text-gray-900">{p.value}</span>
        </div>
      ))}
    </div>
  )
}

function OverviewTab() {
  const { getStats, getRatingDistribution, getTopMentions, getCategoryScores, selectMention, selectedMention } = useHotelStore()
  const stats = getStats()
  const ratingDist = getRatingDistribution()
  const topMentions = getTopMentions()
  const categories = getCategoryScores()

  if (!stats) return null

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Reviews', value: stats.total, icon: MessageSquare, color: '#2563EB', bg: '#DBEAFE' },
          { label: 'Avg Rating', value: `${stats.avgRating}/5`, icon: Star, color: '#D97706', bg: '#FEF3C7' },
          { label: 'Satisfaction', value: `${stats.satisfactionRate}%`, icon: ThumbsUp, color: '#28C76F', bg: '#DCFCE7' },
          { label: 'Negative', value: stats.sentimentCounts.negative, icon: ThumbsDown, color: '#EA5455', bg: '#FEE2E2' },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card-3d-sm p-5"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-500">{label}</span>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: bg }}>
                <Icon size={14} style={{ color }} />
              </div>
            </div>
            <div className="text-2xl font-bold" style={{ color: '#1E293B', fontFamily: 'DM Sans, sans-serif' }}>
              {value}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rating Distribution */}
        <div className="card-3d-sm p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Rating Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={ratingDist}>
              <XAxis dataKey="rating" tick={{ fontSize: 11, fill: '#64748B' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748B' }} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {ratingDist.map((entry, i) => (
                  <Cell key={i} fill={entry.rating >= 4 ? '#28C76F' : entry.rating >= 3 ? '#FFB547' : '#EA5455'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Mentions */}
        <div className="card-3d-sm p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Top Guest Mentions</h3>
          <div className="space-y-2 max-h-[200px] overflow-y-auto">
            {topMentions.map(({ mention, count }, i) => (
              <button
                key={mention}
                onClick={() => { selectMention(mention); }}
                className={clsx(
                  "flex items-center justify-between w-full text-left px-2 py-1 rounded-lg transition-all",
                  selectedMention === mention ? "bg-orange-50 ring-1 ring-orange-300" : "hover:bg-gray-50"
                )}
              >
                <span className="text-xs text-gray-700 truncate max-w-[200px]">{mention}</span>
                <div className="flex items-center gap-2">
                  <div className="h-2 rounded-full bg-gray-100" style={{ width: '80px' }}>
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${(count / (topMentions[0]?.count || 1)) * 100}%`,
                        background: '#FF7A00',
                      }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-gray-500 w-6 text-right">{count}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Category quick view */}
      <div className="card-3d-sm p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Category Performance</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {categories.slice(0, 10).map(cat => (
            <div key={cat.category} className="text-center p-3 rounded-xl border" style={{ borderColor: '#E5E7EB' }}>
              <div className="text-xs text-gray-500 mb-1">{cat.category}</div>
              <div className="text-lg font-bold" style={{ color: cat.score > 50 ? '#28C76F' : cat.score > 25 ? '#FFB547' : '#EA5455' }}>
                {cat.score}%
              </div>
              <div className="text-[10px] text-gray-400">{cat.total} mentions</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SentimentTab() {
  const { getSentimentDistribution, reviews } = useHotelStore()
  const distribution = getSentimentDistribution()
  const total = reviews.length || 1

  return (
    <div className="space-y-6">
      {/* Sentiment cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {distribution.map(({ name, value, percentage }) => (
          <motion.div
            key={name}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-5 rounded-xl border"
            style={{ background: SENTIMENT_BG[name] || '#F8FAFC', borderColor: SENTIMENT_COLORS[name] + '40' }}
          >
            <div className="text-xs font-medium capitalize mb-1" style={{ color: SENTIMENT_COLORS[name] }}>
              {name}
            </div>
            <div className="text-2xl font-bold" style={{ color: '#1E293B' }}>{value}</div>
            <div className="text-xs text-gray-500">{percentage}% of total</div>
          </motion.div>
        ))}
      </div>

      {/* Pie chart */}
      <div className="card-3d-sm p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Sentiment Breakdown</h3>
        <div className="flex items-center justify-center">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={distribution}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                innerRadius={50}
                paddingAngle={2}
              >
                {distribution.map((entry) => (
                  <Cell key={entry.name} fill={SENTIMENT_COLORS[entry.name] || '#94A3B8'} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-center gap-4 mt-4">
          {distribution.map(({ name }) => (
            <div key={name} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ background: SENTIMENT_COLORS[name] }} />
              <span className="text-xs capitalize text-gray-600">{name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Sentiment over confidence */}
      <div className="card-3d-sm p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Confidence Distribution</h3>
        <div className="space-y-2">
          {['High (>0.8)', 'Medium (0.5-0.8)', 'Low (<0.5)'].map((label, i) => {
            const ranges = [[0.8, 1], [0.5, 0.8], [0, 0.5]]
            const count = reviews.filter(r => r.confidence >= ranges[i][0] && r.confidence < ranges[i][1]).length
            const pct = Math.round((count / total) * 100)
            return (
              <div key={label} className="flex items-center gap-3">
                <span className="text-xs text-gray-500 w-[100px]">{label}</span>
                <div className="flex-1 h-3 rounded-full bg-gray-100">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${pct}%`, background: i === 0 ? '#28C76F' : i === 1 ? '#FFB547' : '#EA5455' }}
                  />
                </div>
                <span className="text-xs font-semibold text-gray-600 w-10 text-right">{pct}%</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function CategoriesTab() {
  const { getCategoryScores } = useHotelStore()
  const categories = getCategoryScores()

  const radarData = categories.map(c => ({
    category: c.category,
    score: c.score,
  }))

  return (
    <div className="space-y-6">
      {/* Radar chart */}
      <div className="card-3d-sm p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Category Radar</h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#E5E7EB" />
            <PolarAngleAxis dataKey="category" tick={{ fontSize: 11, fill: '#64748B' }} />
            <Radar
              dataKey="score"
              stroke="#FF7A00"
              fill="#FF7A00"
              fillOpacity={0.2}
              strokeWidth={2}
            />
            <Tooltip content={<ChartTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Category breakdown cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {categories.map(cat => (
          <div key={cat.category} className="card-3d-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-gray-900">{cat.category}</h4>
              <span
                className="text-xs font-bold px-2 py-0.5 rounded-full"
                style={{
                  background: cat.score > 50 ? '#DCFCE7' : cat.score > 25 ? '#FEF3C7' : '#FEE2E2',
                  color: cat.score > 50 ? '#15803D' : cat.score > 25 ? '#B45309' : '#B91C1C',
                }}
              >
                {cat.score}% positive
              </span>
            </div>
            <div className="flex gap-2 h-4 rounded-full overflow-hidden bg-gray-100">
              <div
                className="h-full rounded-l-full transition-all"
                style={{ width: `${(cat.positive / (cat.total || 1)) * 100}%`, background: '#28C76F' }}
              />
              <div
                className="h-full transition-all"
                style={{ width: `${(cat.neutral / (cat.total || 1)) * 100}%`, background: '#FFB547' }}
              />
              <div
                className="h-full rounded-r-full transition-all"
                style={{ width: `${(cat.negative / (cat.total || 1)) * 100}%`, background: '#EA5455' }}
              />
            </div>
            <div className="flex justify-between mt-2 text-[10px] text-gray-500">
              <span>Positive: {cat.positive}</span>
              <span>Neutral: {cat.neutral}</span>
              <span>Negative: {cat.negative}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ReviewsTab() {
  const { getFilteredReviews, selectedSentiment, setSelectedSentiment, searchQuery, setSearchQuery, selectMention, clearMention, selectedMention, mentionReviews, mentionLoading } = useHotelStore()
  const reviews = selectedMention ? mentionReviews : getFilteredReviews()

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center border rounded-xl px-3 py-2 bg-white" style={{ borderColor: '#E5E7EB' }}>
          <Search size={14} className="text-gray-400 mr-2" />
          <input
            type="text"
            placeholder="Search reviews..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="text-sm outline-none w-[200px] bg-transparent"
          />
        </div>
        <div className="flex gap-1">
          {['all', 'positive', 'neutral', 'negative'].map(s => (
            <button
              key={s}
              onClick={() => setSelectedSentiment(s)}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-xs font-medium transition-all capitalize',
                selectedSentiment === s
                  ? 'text-white shadow-sm'
                  : 'text-gray-600 bg-gray-100 hover:bg-gray-200'
              )}
              style={selectedSentiment === s ? { background: s === 'all' ? '#FF7A00' : SENTIMENT_COLORS[s] || '#FF7A00' } : {}}
            >
              {s}
            </button>
          ))}
        </div>
        <span className="text-xs text-gray-500 ml-auto">{reviews.length} reviews</span>
      </div>

      {/* Active mention filter indicator */}
      {selectedMention && (
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-orange-50 border border-orange-200">
          <span className="text-xs text-orange-800">
            Showing reviews mentioning: <strong>"{selectedMention}"</strong>
          </span>
          <button
            onClick={clearMention}
            className="ml-auto text-xs text-orange-600 hover:text-orange-900 underline"
          >
            Clear filter
          </button>
          {mentionLoading && <Loader2 size={12} className="animate-spin text-orange-500" />}
        </div>
      )}

      {/* Reviews list */}
      <div className="space-y-3">
        {reviews.slice(0, 50).map((review, i) => (
          <motion.div
            key={review._id || i}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.02 }}
            className="card-3d-sm p-4"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-0.5">
                  {[1, 2, 3, 4, 5].map(star => (
                    <Star
                      key={star}
                      size={12}
                      fill={star <= review.rating ? '#D97706' : 'none'}
                      stroke={star <= review.rating ? '#D97706' : '#CBD5E1'}
                    />
                  ))}
                </div>
                <span className="text-xs text-gray-500">{review.rating}/5</span>
              </div>
              <span
                className="text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize"
                style={{
                  background: SENTIMENT_BG[review.sentiment] || '#F1F5F9',
                  color: SENTIMENT_COLORS[review.sentiment] || '#64748B',
                }}
              >
                {review.sentiment}
              </span>
            </div>
            {review.title && (
              <p className="text-xs font-semibold text-gray-900 mb-1">{review.title}</p>
            )}
            <p className="text-xs text-gray-700 leading-relaxed line-clamp-3">{review.text}</p>
            {review.mentions?.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {review.mentions.slice(0, 5).map(m => (
                  <button
                    key={m}
                    onClick={() => selectMention(m)}
                    className={clsx(
                      'text-[10px] px-2 py-0.5 rounded-full transition-all cursor-pointer',
                      selectedMention === m
                        ? 'bg-orange-500 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-orange-100 hover:text-orange-700'
                    )}
                  >
                    {m}
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function InsightsTab() {
  const { getInsights } = useHotelStore()
  const insights = getInsights()

  const typeConfig = {
    warning: { icon: AlertTriangle, color: '#D97706', bg: '#FEF3C7', border: '#FDE68A' },
    success: { icon: CheckCircle, color: '#28C76F', bg: '#DCFCE7', border: '#BBF7D0' },
    alert: { icon: AlertTriangle, color: '#EA5455', bg: '#FEE2E2', border: '#FECACA' },
  }

  if (!insights.length) {
    return (
      <div className="text-center py-16">
        <Zap size={40} className="mx-auto mb-3 text-gray-300" />
        <p className="text-sm text-gray-500">Not enough data to generate insights yet.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="text-xs text-gray-500 mb-2">{insights.length} actionable insights generated</div>
      {insights.map((insight, i) => {
        const config = typeConfig[insight.type] || typeConfig.alert
        const Icon = config.icon
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="p-4 rounded-xl border"
            style={{ background: config.bg, borderColor: config.border }}
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                <Icon size={16} style={{ color: config.color }} />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-gray-900">{insight.title}</h4>
                  <span
                    className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded"
                    style={{ background: config.color + '20', color: config.color }}
                  >
                    {insight.priority}
                  </span>
                </div>
                <p className="text-xs text-gray-600 leading-relaxed">{insight.description}</p>
              </div>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

export default function HotelDashboardPage() {
  const { loading, error, reviews, activeTab, setActiveTab, loadReviews } = useHotelStore()

  useEffect(() => {
    loadReviews()
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <Loader2 size={32} className="animate-spin text-orange-500" />
        <p className="text-sm text-gray-500">Loading hotel reviews...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <AlertTriangle size={32} className="text-red-500" />
        <p className="text-sm text-gray-500">{error}</p>
      </div>
    )
  }

  if (!reviews.length) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <MessageSquare size={32} className="text-gray-300" />
        <p className="text-sm text-gray-500">No reviews found. Process hotel reviews first.</p>
      </div>
    )
  }

  const tabContent = {
    overview: <OverviewTab />,
    sentiment: <SentimentTab />,
    categories: <CategoriesTab />,
    reviews: <ReviewsTab />,
    insights: <InsightsTab />,
  }

  return (
    <div className="min-h-screen" style={{ background: '#F8FAFC' }}>
      {/* Header */}
      <div
        className="sticky top-0 z-20 px-6 pt-4 pb-0"
        style={{
          background: 'rgba(248,250,252,0.95)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid #E5E7EB',
          boxShadow: '0 1px 8px rgba(0,0,0,0.06)',
        }}
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <motion.h1
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              className="font-bold text-2xl"
              style={{ color: '#1E293B', fontFamily: 'DM Sans, sans-serif' }}
            >
              Marriott Hotel Reviews
            </motion.h1>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xs text-gray-400">
                Courtyard by Marriott · New York Manhattan/Fifth Avenue
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full font-semibold" style={{ background: '#DBEAFE', color: '#2563EB' }}>
                {reviews.length} reviews
              </span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 overflow-x-auto pb-0" style={{ scrollbarWidth: 'none' }}>
          {TABS.map(({ id, label, icon: Icon }) => {
            const isActive = activeTab === id
            return (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className="flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold transition-all whitespace-nowrap"
                style={{
                  color: isActive ? '#FF7A00' : '#64748B',
                  borderBottom: isActive ? '2px solid #FF7A00' : '2px solid transparent',
                  background: 'transparent',
                }}
              >
                <Icon size={13} />
                {label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            {tabContent[activeTab]}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
