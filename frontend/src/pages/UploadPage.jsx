import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Zap, AlertCircle, CheckCircle, Loader2, Brain, ChevronDown, FileText, Activity, TrendingUp, BarChart3, Link2, Search } from 'lucide-react'
import { useReviewStore } from '../store/reviewStore'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import axios from 'axios'

const TABS = ['Upload File', 'Paste Text', 'Demo Dataset', 'Scrape URL']

const AGENT_STEPS = [
  { name: 'Preprocessing',     color: '#2563EB', bg: '#DBEAFE', icon: FileText },
  { name: 'Deduplication',     color: '#7C3AED', bg: '#EDE9FE', icon: Activity },
  { name: 'Sentiment AI',      color: '#28C76F', bg: '#DCFCE7', icon: Brain },
  { name: 'Trend Detection',   color: '#D97706', bg: '#FEF3C7', icon: TrendingUp },
  { name: 'Recommendations',   color: '#EA5455', bg: '#FEE2E2', icon: Zap },
  { name: 'Report Synthesis',  color: '#0891B2', bg: '#ECFEFF', icon: BarChart3 },
]

function AgentPipelineVisual({ status }) {
  return (
    <div className="card-3d p-6 mt-6">
      <div className="text-xs font-bold uppercase tracking-wider mb-4" style={{ color: '#94A3B8' }}>
        LangGraph Pipeline Running
      </div>
      <div className="flex flex-col gap-3">
        {AGENT_STEPS.map(({ name, color, bg, icon: Icon }, i) => (
          <div key={name} className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: bg, border: `1px solid ${color}30` }}>
              <Icon size={14} style={{ color }} />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium" style={{ color: '#1E293B' }}>{name}</span>
                {status === 'running' && (
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.35 }}
                    className="text-xs font-semibold"
                    style={{ color }}
                  >
                    processing…
                  </motion.div>
                )}
              </div>
              <div className="h-1.5 rounded-full overflow-hidden" style={{ background: '#F1F5F9' }}>
                {status === 'running' && (
                  <motion.div
                    className="h-full rounded-full"
                    initial={{ width: '0%' }}
                    animate={{ width: ['0%', '70%', '100%'] }}
                    transition={{ duration: 4, delay: i * 1.1, ease: 'easeInOut' }}
                    style={{ background: color }}
                  />
                )}
                {status === 'complete' && (
                  <div className="h-full rounded-full w-full" style={{ background: color }} />
                )}
              </div>
            </div>
            {status === 'complete' && (
              <CheckCircle size={14} style={{ color: '#28C76F', flexShrink: 0 }} />
            )}
            {status === 'running' && i === 0 && (
              <Loader2 size={14} className="animate-spin flex-shrink-0" style={{ color }} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function UploadPage() {
  const navigate   = useNavigate()
  const { jobStatus, startDemoAnalysis, startFileAnalysis, startTextAnalysis, startPasteAnalysis } = useReviewStore()

  const [activeTab, setActiveTab]     = useState(0)
  const [file, setFile]               = useState(null)
  const [pasteText, setPasteText]     = useState('')
  const [category, setCategory]       = useState('General')
  const [productName, setProductName] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Scrape URL state
  const [scrapeUrl, setScrapeUrl]           = useState('')
  const [scrapeMaxReviews, setScrapeMaxReviews] = useState(50)
  const [scrapePhase, setScrapePhase]       = useState('idle') // idle | scraping | found | error
  const [scrapeResult, setScrapeResult]     = useState(null)
  const [scrapeError, setScrapeError]       = useState('')

  const onDrop = useCallback((accepted) => {
    if (accepted[0]) setFile(accepted[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'], 'application/json': ['.json'] },
    maxFiles: 1,
  })

  const detectPlatform = (url) => {
    const u = url.toLowerCase()
    if (u.includes('amazon.in') || u.includes('amazon.com') || u.includes('amzn')) return 'amazon'
    if (u.includes('flipkart.com')) return 'flipkart'
    return null
  }

  const platform = detectPlatform(scrapeUrl)

  const handleScrapeAndAnalyze = async () => {
    if (!scrapeUrl.trim()) return toast.error('Please paste a product URL')
    if (!platform) return toast.error('Only Amazon.in and Flipkart URLs are supported')
    setScrapePhase('scraping')
    setScrapeError('')
    setScrapeResult(null)
    try {
      const { data } = await axios.post('/api/scrape', {
        url: scrapeUrl.trim(),
        max_reviews: scrapeMaxReviews,
      })
      setScrapeResult(data)
      setScrapePhase('found')
      toast.success(`Found ${data.scraped_count} reviews — sending to pipeline…`)
      await startPasteAnalysis(data.reviews)
      navigate('/dashboard')
    } catch (e) {
      setScrapePhase('error')
      setScrapeError(e?.response?.data?.detail || 'Scraping failed. Check the URL and try again.')
      toast.error('Scraping failed')
    }
  }

  const isProcessing = jobStatus === 'running' || jobStatus === 'queued'

  const handleAnalyze = async () => {
    try {
      if (activeTab === 0) {
        if (!file) return toast.error('Please upload a file first')
        await startFileAnalysis(file, category, productName || 'Unknown Product')
        toast.success(`Analyzing ${file.name}…`)
      } else if (activeTab === 1) {
        if (!pasteText.trim()) return toast.error('Please paste some review text')
        await startTextAnalysis(pasteText, category, productName || 'Unknown Product')
        toast.success('Analysis started!')
      } else if (activeTab === 2) {
        await startDemoAnalysis()
        toast.success('Running demo analysis with 247 synthetic reviews…')
      } else {
        // Scrape URL tab — handled by its own button
        return
      }
      navigate('/dashboard')
    } catch (e) {
      toast.error('Failed to start analysis. Is the backend running?')
    }
  }

  return (
    <div className="min-h-screen p-8" style={{ background: '#F8FAFC' }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="font-bold text-3xl mb-2" style={{ color: '#1E293B', fontFamily: 'DM Sans, sans-serif' }}>
          Ingest Reviews
        </h1>
        <p className="text-sm font-medium" style={{ color: '#64748B' }}>
          Upload CSV/JSON, paste raw text, or run the built-in synthetic demo
        </p>
      </motion.div>

      <div className="max-w-3xl">
        {/* Tab switcher */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex gap-1 p-1 rounded-2xl mb-6 inline-flex"
          style={{ background: '#F1F5F9', border: '1px solid #E5E7EB' }}
        >
          {TABS.map((tab, i) => (
            <button
              key={tab}
              onClick={() => setActiveTab(i)}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
              style={activeTab === i ? {
                background: '#FFFFFF',
                color: '#FF7A00',
                border: '1px solid #FED7AA',
                boxShadow: '0 2px 8px rgba(255,122,0,0.12)',
              } : {
                color: '#64748B',
                border: '1px solid transparent',
              }}
            >
              {tab}
            </button>
          ))}
        </motion.div>

        {/* Tab content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.18 }}
          >
            {/* Upload File */}
            {activeTab === 0 && (
              <div className="space-y-4">
                <div
                  {...getRootProps()}
                  className="card-3d p-12 text-center cursor-pointer transition-all"
                  style={isDragActive ? { borderColor: '#FF7A00', boxShadow: '0 0 0 3px rgba(255,122,0,0.12), 0 12px 40px rgba(0,0,0,0.1)' }
                    : file ? { borderColor: '#BBF7D0', background: '#F0FDF4' } : {}}
                >
                  <input {...getInputProps()} />
                  <AnimatePresence mode="wait">
                    {file ? (
                      <motion.div key="file" initial={{ scale: 0.85, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
                        <CheckCircle size={44} className="mx-auto mb-3" style={{ color: '#28C76F' }} />
                        <div className="font-bold text-base mb-1" style={{ color: '#1E293B' }}>{file.name}</div>
                        <div className="text-sm" style={{ color: '#94A3B8' }}>
                          {(file.size / 1024).toFixed(1)} KB · Click to replace
                        </div>
                      </motion.div>
                    ) : (
                      <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
                          style={{ background: isDragActive ? '#FFF3E8' : '#F8FAFC', border: `2px dashed ${isDragActive ? '#FF7A00' : '#CBD5E1'}` }}>
                          <Upload size={28} style={{ color: isDragActive ? '#FF7A00' : '#94A3B8' }} />
                        </div>
                        <div className="font-bold text-base mb-1" style={{ color: '#1E293B' }}>
                          {isDragActive ? 'Drop it here!' : 'Drop CSV or JSON'}
                        </div>
                        <div className="text-sm" style={{ color: '#94A3B8' }}>
                          or click to browse · Supports Amazon/Flipkart exports
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
                <div className="text-xs px-1" style={{ color: '#94A3B8' }}>
                  Expected columns: <span className="font-mono font-semibold" style={{ color: '#FF7A00' }}>review_text</span>, rating, category, product_name, date (flexible naming)
                </div>
              </div>
            )}

            {/* Paste Text */}
            {activeTab === 1 && (
              <div>
                <textarea
                  value={pasteText}
                  onChange={e => setPasteText(e.target.value)}
                  placeholder={"Paste reviews here, one per line...\n\nExamples:\nBattery life is amazing but camera is disappointing\nYaar ye phone bahut acha hai! Highly recommend\nTerrible packaging, product arrived damaged"}
                  rows={12}
                  className="w-full rounded-2xl p-5 text-sm resize-none outline-none transition-all leading-relaxed"
                  style={{
                    background: '#FFFFFF',
                    border: '1px solid #E5E7EB',
                    color: '#1E293B',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  }}
                  onFocus={e => { e.target.style.borderColor = '#FF7A00'; e.target.style.boxShadow = '0 0 0 3px rgba(255,122,0,0.1)' }}
                  onBlur={e  => { e.target.style.borderColor = '#E5E7EB'; e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)' }}
                />
                <div className="text-xs mt-2 px-1 font-medium" style={{ color: '#94A3B8' }}>
                  {pasteText.split('\n').filter(l => l.trim().length > 5).length} reviews detected
                </div>
              </div>
            )}

            {/* Demo Dataset */}
            {activeTab === 2 && (
              <div className="card-3d p-8">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: '#FFF3E8', border: '1.5px solid #FED7AA' }}>
                    <Brain size={22} style={{ color: '#FF7A00' }} />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg mb-2" style={{ color: '#1E293B', fontFamily: 'DM Sans, sans-serif' }}>
                      Synthetic Demo Dataset
                    </h3>
                    <p className="text-sm leading-relaxed mb-4" style={{ color: '#64748B' }}>
                      247 reviews across 3 categories:{' '}
                      <span className="font-semibold" style={{ color: '#2563EB' }}>Smartphones</span>,{' '}
                      <span className="font-semibold" style={{ color: '#7C3AED' }}>Protein Powder</span>, and{' '}
                      <span className="font-semibold" style={{ color: '#28C76F' }}>Bluetooth Earphones</span>.
                    </p>
                    <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                      {[
                        { text: 'Hindi + Hinglish reviews included',   color: '#2563EB', bg: '#DBEAFE' },
                        { text: 'Bot-like reviews for detection',       color: '#EA5455', bg: '#FEE2E2' },
                        { text: 'Exact + near-duplicate reviews',       color: '#D97706', bg: '#FEF3C7' },
                        { text: 'Sarcastic and ambiguous reviews',      color: '#A78BFA', bg: '#EDE9FE' },
                        { text: 'Seeded packaging complaint trend',     color: '#28C76F', bg: '#DCFCE7' },
                        { text: '6 bots + 2 exact duplicates',         color: '#0891B2', bg: '#ECFEFF' },
                      ].map(({ text, color, bg }) => (
                        <div key={text}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium"
                          style={{ background: bg, color }}>
                          ✓ {text}
                        </div>
                      ))}
                    </div>
                    <div className="px-3 py-2.5 rounded-xl text-xs inline-flex items-center gap-2"
                      style={{ background: '#FEF3C7', border: '1px solid #FDE68A', color: '#B45309' }}>
                      <AlertCircle size={12} />
                      Packaging complaints are seeded to spike in last 50 earphone reviews — verify the system detects it!
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Scrape URL tab */}
            {activeTab === 3 && (
              <div className="space-y-4">
                {/* URL input */}
                <div>
                  <label className="text-xs font-semibold mb-1.5 block" style={{ color: '#475569' }}>
                    Product Page URL
                  </label>
                  <div className="relative">
                    <div className="absolute left-4 top-1/2 -translate-y-1/2">
                      <Link2 size={15} style={{ color: '#94A3B8' }} />
                    </div>
                    <input
                      value={scrapeUrl}
                      onChange={e => { setScrapeUrl(e.target.value); setScrapePhase('idle'); setScrapeError('') }}
                      placeholder="Paste Amazon.in or Flipkart product URL…"
                      className="w-full rounded-2xl pl-10 pr-4 py-3.5 text-sm outline-none transition-all"
                      style={{
                        background: '#FFFFFF',
                        border: '1px solid #E5E7EB',
                        color: '#1E293B',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                      }}
                      onFocus={e => { e.target.style.borderColor = '#FF7A00'; e.target.style.boxShadow = '0 0 0 3px rgba(255,122,0,0.1)' }}
                      onBlur={e  => { e.target.style.borderColor = '#E5E7EB'; e.target.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)' }}
                    />
                  </div>

                  {/* Platform badge */}
                  <AnimatePresence>
                    {scrapeUrl && (
                      <motion.div
                        initial={{ opacity: 0, y: -4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -4 }}
                        className="flex items-center gap-2 mt-2"
                      >
                        {platform === 'amazon' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
                            style={{ background: '#FFF3E8', color: '#FF7A00', border: '1px solid #FED7AA' }}>
                            🟠 Amazon.in detected
                          </span>
                        )}
                        {platform === 'flipkart' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
                            style={{ background: '#EFF6FF', color: '#2563EB', border: '1px solid #BFDBFE' }}>
                            🔵 Flipkart detected
                          </span>
                        )}
                        {scrapeUrl && !platform && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
                            style={{ background: '#FEF2F2', color: '#DC2626', border: '1px solid #FECACA' }}>
                            ⚠️ Unsupported platform — use Amazon.in or Flipkart
                          </span>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Max reviews select */}
                <div>
                  <label className="text-xs font-semibold mb-1.5 block" style={{ color: '#475569' }}>
                    Max Reviews to Scrape
                  </label>
                  <div className="flex gap-2">
                    {[25, 50, 100].map(n => (
                      <button
                        key={n}
                        onClick={() => setScrapeMaxReviews(n)}
                        className="px-5 py-2 rounded-xl text-sm font-semibold transition-all"
                        style={scrapeMaxReviews === n ? {
                          background: '#FF7A00',
                          color: '#FFFFFF',
                          boxShadow: '0 2px 8px rgba(255,122,0,0.3)',
                        } : {
                          background: '#FFFFFF',
                          color: '#64748B',
                          border: '1px solid #E5E7EB',
                        }}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Phase indicators */}
                <AnimatePresence>
                  {scrapePhase === 'scraping' && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="rounded-xl p-4 flex items-center gap-3"
                      style={{ background: '#FFF3E8', border: '1px solid #FED7AA' }}
                    >
                      <Loader2 size={16} className="animate-spin flex-shrink-0" style={{ color: '#FF7A00' }} />
                      <div>
                        <div className="text-sm font-semibold" style={{ color: '#FF7A00' }}>
                          Scraping reviews…
                        </div>
                        <div className="text-xs mt-0.5" style={{ color: '#92400E' }}>
                          Connecting to {platform === 'amazon' ? 'Amazon.in' : 'Flipkart'} — this may take a few seconds
                        </div>
                      </div>
                    </motion.div>
                  )}
                  {scrapePhase === 'found' && scrapeResult && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="rounded-xl p-4 flex items-center gap-3"
                      style={{ background: '#F0FDF4', border: '1px solid #86EFAC' }}
                    >
                      <CheckCircle size={16} className="flex-shrink-0" style={{ color: '#16A34A' }} />
                      <div>
                        <div className="text-sm font-semibold" style={{ color: '#16A34A' }}>
                          Found {scrapeResult.scraped_count} reviews for "{scrapeResult.product_name}"
                        </div>
                        <div className="text-xs mt-0.5" style={{ color: '#15803D' }}>
                          {scrapeResult.used_fallback
                            ? 'Using representative sample data · Sending to analysis pipeline…'
                            : 'Live scrape successful · Sending to analysis pipeline…'}
                        </div>
                      </div>
                    </motion.div>
                  )}
                  {scrapePhase === 'error' && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="rounded-xl p-4 flex items-center gap-3"
                      style={{ background: '#FEF2F2', border: '1px solid #FECACA' }}
                    >
                      <AlertCircle size={16} className="flex-shrink-0" style={{ color: '#DC2626' }} />
                      <div className="text-sm" style={{ color: '#DC2626' }}>
                        {scrapeError || 'Scraping failed. Check the URL and try again.'}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Scrape CTA */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleScrapeAndAnalyze}
                  disabled={isProcessing || scrapePhase === 'scraping' || !scrapeUrl || !platform}
                  className="w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-bold text-base transition-all disabled:opacity-50 disabled:cursor-not-allowed text-white"
                  style={{
                    background: (isProcessing || scrapePhase === 'scraping') ? '#94A3B8' : '#FF7A00',
                    boxShadow: (isProcessing || scrapePhase === 'scraping') ? 'none' : '0 6px 24px rgba(255,122,0,0.35)',
                  }}
                >
                  {(isProcessing || scrapePhase === 'scraping') ? (
                    <><Loader2 size={18} className="animate-spin" /> {scrapePhase === 'scraping' ? 'Scraping…' : 'Running Pipeline…'}</>
                  ) : (
                    <><Search size={18} /> Scrape & Analyze</>
                  )}
                </motion.button>

                {/* Info note */}
                <div className="text-xs text-center px-4" style={{ color: '#94A3B8' }}>
                  If live scraping is blocked, a representative review sample is used automatically — analysis always succeeds.
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Advanced config — only for tabs 0 and 1 */}
        {(activeTab === 0 || activeTab === 1) && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="mt-4">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2 text-sm mb-3 font-medium"
              style={{ color: '#64748B' }}
            >
              <ChevronDown size={14} className={clsx('transition-transform', showAdvanced ? 'rotate-180' : '')} />
              Advanced options
            </button>
            <AnimatePresence>
              {showAdvanced && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="grid grid-cols-2 gap-4 overflow-hidden"
                >
                  {[
                    { label: 'Product Category', value: category,    setter: setCategory,    placeholder: 'e.g. Smartphone' },
                    { label: 'Product Name',     value: productName, setter: setProductName, placeholder: 'e.g. Samsung Galaxy S24' },
                  ].map(({ label, value, setter, placeholder }) => (
                    <div key={label}>
                      <label className="text-xs font-semibold mb-1.5 block" style={{ color: '#475569' }}>{label}</label>
                      <input
                        value={value}
                        onChange={e => setter(e.target.value)}
                        placeholder={placeholder}
                        className="w-full rounded-xl px-4 py-2.5 text-sm outline-none transition-all"
                        style={{ background: '#FFFFFF', border: '1px solid #E5E7EB', color: '#1E293B' }}
                        onFocus={e => { e.target.style.borderColor = '#FF7A00'; e.target.style.boxShadow = '0 0 0 3px rgba(255,122,0,0.1)' }}
                        onBlur={e  => { e.target.style.borderColor = '#E5E7EB'; e.target.style.boxShadow = 'none' }}
                      />
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* CTA — not shown on Scrape URL tab (it has its own button) */}
        {activeTab !== 3 && (
          <>
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAnalyze}
            disabled={isProcessing}
            className="mt-6 w-full flex items-center justify-center gap-3 py-4 rounded-2xl font-bold text-base transition-all disabled:opacity-50 disabled:cursor-not-allowed text-white"
            style={{
              background: isProcessing ? '#94A3B8' : '#FF7A00',
              boxShadow: isProcessing ? 'none' : '0 6px 24px rgba(255,122,0,0.35), 0 2px 8px rgba(255,122,0,0.2)',
            }}
          >
            {isProcessing ? (
              <><Loader2 size={18} className="animate-spin" /> Running Pipeline…</>
            ) : (
              <><Zap size={18} /> Launch Analysis Pipeline</>
            )}
          </motion.button>

          {/* Pipeline visual when running */}
          {isProcessing && <AgentPipelineVisual status={jobStatus} />}
          </>
        )}
      </div>
    </div>
  )
}
