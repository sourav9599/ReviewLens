import { useNavigate } from 'react-router-dom'
import { motion, useMotionValue, useTransform } from 'framer-motion'
import { Brain, TrendingUp, Shield, Zap, BarChart3, Globe, ArrowRight, Sparkles } from 'lucide-react'
import { useEffect, useRef } from 'react'

const FEATURES = [
  { icon: Brain, title: 'Orchestrator Agent', desc: 'Controller agent with dynamic decision making, feedback loops & conditional routing via LangGraph', color: '#bf5af2' },
  { icon: Shield, title: 'Advanced Bot Detection', desc: 'Risk-level scoring (low/medium/high/critical) with 9 heuristic signals and spam pattern matching', color: '#ff3b3b' },
  { icon: TrendingUp, title: 'Time-Series Anomaly', desc: 'Z-score statistical anomaly detection surfaces emerging complaint spikes early with confidence bounds', color: '#39ff14' },
  { icon: Globe, title: 'Multilingual AI', desc: 'Handles English, Hindi, Hinglish and regional Indian languages with per-language sentiment analysis', color: '#ffb800' },
  { icon: BarChart3, title: 'Emoji Intelligence', desc: 'Full emoji → sentiment mapping with confidence boosting. 60+ emojis decoded as emotional signals', color: '#ff006e' },
  { icon: Zap, title: 'Cross-Product Compare', desc: '3+ category side-by-side analysis: radar charts, sentiment rankings, and bot rate comparison', color: '#00f5ff' },
]

const glassCard = {
  background: 'rgba(255, 255, 255, 0.04)',
  border: '1px solid rgba(255, 255, 255, 0.10)',
  borderRadius: '16px',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
}

function ParticleField() {
  const canvasRef = useRef(null)
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const particles = Array.from({ length: 80 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      r: Math.random() * 1.5 + 0.5,
      alpha: Math.random() * 0.4 + 0.1,
      color: Math.random() > 0.5 ? '0,245,255' : '191,90,242',
    }))

    let animId
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy
        if (p.x < 0) p.x = canvas.width
        if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        if (p.y > canvas.height) p.y = 0
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(${p.color},${p.alpha})`
        ctx.fill()
      })
      particles.forEach((a, i) => {
        particles.slice(i + 1).forEach(b => {
          const d = Math.hypot(a.x - b.x, a.y - b.y)
          if (d < 100) {
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.strokeStyle = `rgba(0,245,255,${0.05 * (1 - d / 100)})`
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        })
      })
      animId = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(animId)
  }, [])
  return <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} />
}

function AgentFlowDiagram() {
  const agents = ['Orchestrator', 'Emoji AI', 'Dedup+Bots', 'Sentiment', 'Trends', 'Cross-Compare', 'Recommend', 'Report']
  const colors = ['#bf5af2', '#ffb800', '#39ff14', '#ff006e', '#ff3b3b', '#00f5ff', '#ffb800', '#39ff14']
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexWrap: 'wrap', justifyContent: 'center' }}>
      {agents.map((a, i) => (
        <div key={a} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 + i * 0.10 }}
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              fontSize: '11px',
              fontFamily: 'monospace',
              fontWeight: 600,
              whiteSpace: 'nowrap',
              background: `${colors[i]}15`,
              border: `1px solid ${colors[i]}50`,
              color: colors[i],
            }}
          >
            {a}
          </motion.div>
          {i < agents.length - 1 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 + i * 0.10 }}
              style={{ color: 'rgba(255,255,255,0.5)', fontSize: '10px' }}
            >→</motion.div>
          )}
        </div>
      ))}
    </div>
  )
}

export default function LandingPage() {
  const navigate = useNavigate()
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const rotateX = useTransform(mouseY, [-300, 300], [5, -5])
  const rotateY = useTransform(mouseX, [-300, 300], [-5, 5])

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    mouseX.set(e.clientX - rect.left - rect.width / 2)
    mouseY.set(e.clientY - rect.top - rect.height / 2)
  }

  return (
    <div
      onMouseMove={handleMouseMove}
      style={{
        minHeight: '100vh',
        background: '#0a0a0f',
        position: 'relative',
        overflow: 'hidden',
        backgroundImage: `
          linear-gradient(rgba(0,245,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,245,255,0.03) 1px, transparent 1px)
        `,
        backgroundSize: '40px 40px',
      }}
    >
      <ParticleField />

      {/* Ambient blobs */}
      <div style={{
        position: 'absolute', top: '25%', left: '25%',
        width: '384px', height: '384px', borderRadius: '50%',
        opacity: 0.06, filter: 'blur(80px)', pointerEvents: 'none',
        background: 'radial-gradient(circle, #00f5ff, transparent)',
      }} />
      <div style={{
        position: 'absolute', bottom: '25%', right: '25%',
        width: '384px', height: '384px', borderRadius: '50%',
        opacity: 0.06, filter: 'blur(80px)', pointerEvents: 'none',
        background: 'radial-gradient(circle, #bf5af2, transparent)',
      }} />

      {/* Top nav */}
      <nav style={{
        position: 'relative', zIndex: 10,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 32px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'linear-gradient(135deg, rgba(0,245,255,0.2), rgba(191,90,242,0.2))',
            border: '1px solid rgba(0,245,255,0.3)',
          }}>
            <Brain size={16} style={{ color: '#00f5ff' }} />
          </div>
          <span style={{ fontWeight: 700, color: '#ffffff', fontSize: '16px' }}>ReviewIQ</span>
          <span style={{
            padding: '2px 8px', borderRadius: '6px', fontSize: '11px', fontFamily: 'monospace',
            background: 'rgba(191,90,242,0.1)', color: '#bf5af2', border: '1px solid rgba(191,90,242,0.2)',
          }}>
            v2.0 Agentic
          </span>
        </div>
        <button
          onClick={() => navigate('/analyze')}
          style={{
            background: 'transparent', border: '1px solid rgba(255,255,255,0.15)',
            color: 'rgba(255,255,255,0.8)', padding: '8px 20px', borderRadius: '10px',
            fontSize: '14px', cursor: 'pointer', transition: 'all 0.2s',
          }}
          onMouseEnter={e => { e.target.style.borderColor = 'rgba(0,245,255,0.4)'; e.target.style.color = '#fff' }}
          onMouseLeave={e => { e.target.style.borderColor = 'rgba(255,255,255,0.15)'; e.target.style.color = 'rgba(255,255,255,0.8)' }}
        >
          Launch App
        </button>
      </nav>

      {/* Hero */}
      <div style={{
        position: 'relative', zIndex: 10,
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        textAlign: 'center', padding: '64px 24px 80px',
      }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '8px',
            padding: '8px 16px', borderRadius: '999px', marginBottom: '32px',
            fontSize: '13px', background: 'rgba(191,90,242,0.08)',
            border: '1px solid rgba(191,90,242,0.25)', color: '#bf5af2',
          }}
        >
          <Sparkles size={14} />
          <span>Powered by LangGraph × Ollama — 9-Agent Agentic Architecture</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.7 }}
          style={{
            fontWeight: 800, fontSize: 'clamp(2.5rem, 6vw, 4.5rem)',
            color: '#ffffff', lineHeight: 1.05, marginBottom: '24px',
            maxWidth: '900px', letterSpacing: '-0.02em',
          }}
        >
          Turn Reviews Into{' '}
          <span style={{
            background: 'linear-gradient(135deg, #00f5ff, #bf5af2)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
            Intelligence
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.7 }}
          style={{
            fontSize: '18px', maxWidth: '640px', marginBottom: '16px',
            lineHeight: 1.7, color: 'rgba(255,255,255,0.75)',
          }}
        >
          A 6-agent AI pipeline that ingests thousands of customer reviews, extracts
          granular feature-level sentiment, detects emerging complaint patterns, and
          surfaces prioritized recommendations — in real time.
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          style={{ marginBottom: '40px' }}
        >
          <AgentFlowDiagram />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px', justifyContent: 'center' }}
        >
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/analyze')}
            style={{
              display: 'flex', alignItems: 'center', gap: '10px',
              padding: '14px 32px', borderRadius: '16px',
              fontWeight: 600, fontSize: '15px', cursor: 'pointer',
              background: 'linear-gradient(135deg, rgba(0,245,255,0.2), rgba(191,90,242,0.2))',
              border: '1px solid rgba(0,245,255,0.4)', color: '#ffffff',
              boxShadow: '0 0 30px rgba(0,245,255,0.15)',
              transition: 'all 0.2s',
            }}
          >
            <Zap size={18} style={{ color: '#00f5ff' }} />
            Start Analyzing
            <ArrowRight size={16} />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/analyze')}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '14px 32px', borderRadius: '16px',
              fontWeight: 600, fontSize: '15px', cursor: 'pointer',
              background: 'transparent',
              border: '1px solid rgba(255,255,255,0.15)', color: 'rgba(255,255,255,0.8)',
              transition: 'all 0.2s',
            }}
          >
            Try Demo Dataset →
          </motion.button>
        </motion.div>

        {/* 3D mock dashboard card */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          style={{ rotateX, rotateY, perspective: 1000, marginTop: '80px', width: '100%', maxWidth: '900px' }}
        >
          <div style={{
            ...glassCard,
            padding: '24px',
            boxShadow: '0 0 40px rgba(0,245,255,0.08), 0 0 80px rgba(0,245,255,0.04)',
          }}>
            {/* Window chrome */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', gap: '6px' }}>
                {['#ff5f57', '#ffbd2e', '#28c840'].map(c => (
                  <div key={c} style={{ width: '12px', height: '12px', borderRadius: '50%', background: c }} />
                ))}
              </div>
              <div style={{ flex: 1, height: '20px', borderRadius: '999px', background: 'rgba(255,255,255,0.04)' }} />
              <span style={{ fontSize: '11px', fontFamily: 'monospace', color: 'rgba(255,255,255,0.5)' }}>
                reviewiq.app/dashboard
              </span>
            </div>

            {/* Stat cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
              {[
                { label: 'Reviews Analyzed', val: '247', color: '#00f5ff' },
                { label: 'Alerts Detected', val: '3', color: '#ff3b3b' },
                { label: 'Avg Sentiment', val: '68%', color: '#39ff14' },
                { label: 'Recommendations', val: '7', color: '#ffb800' },
              ].map(({ label, val, color }) => (
                <div key={label} style={{
                  borderRadius: '12px', padding: '16px', textAlign: 'center',
                  background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
                }}>
                  <div style={{ fontSize: '28px', fontWeight: 700, color, fontFamily: 'system-ui' }}>{val}</div>
                  <div style={{ fontSize: '11px', marginTop: '4px', color: 'rgba(255,255,255,0.6)' }}>{label}</div>
                </div>
              ))}
            </div>

            {/* Chart + alert */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px' }}>
              <div style={{
                borderRadius: '12px', padding: '16px',
                background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
                height: '120px',
              }}>
                <div style={{ fontSize: '11px', marginBottom: '12px', color: 'rgba(255,255,255,0.6)' }}>
                  Feature Sentiment Trend
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '60px' }}>
                  {[40, 65, 55, 80, 45, 90, 35, 72, 58, 88].map((h, i) => (
                    <motion.div key={i}
                      initial={{ height: 0 }}
                      animate={{ height: `${h}%` }}
                      transition={{ delay: 0.8 + i * 0.06 }}
                      style={{
                        flex: 1, borderRadius: '3px 3px 0 0',
                        background: i % 3 === 0
                          ? 'rgba(255,59,59,0.6)'
                          : i % 3 === 1
                          ? 'rgba(57,255,20,0.6)'
                          : 'rgba(0,245,255,0.4)',
                      }}
                    />
                  ))}
                </div>
              </div>
              <div style={{
                borderRadius: '12px', padding: '16px',
                background: 'rgba(255,59,59,0.05)', border: '1px solid rgba(255,59,59,0.2)',
                height: '120px',
              }}>
                <div style={{ fontSize: '11px', marginBottom: '8px', color: '#ff3b3b' }}>⚠ Critical Alert</div>
                <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.75)', lineHeight: 1.6 }}>
                  Packaging complaints up 38% in last 50 earphone reviews
                </div>
                <div style={{ marginTop: '12px', fontSize: '11px', fontFamily: 'monospace', color: '#ffb800' }}>
                  → Systemic Issue
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Features grid */}
      <div style={{
        position: 'relative', zIndex: 10,
        padding: '0 32px 96px', maxWidth: '1152px', margin: '0 auto',
      }}>
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          style={{
            fontSize: '30px', fontWeight: 700, textAlign: 'center',
            color: '#ffffff', marginBottom: '48px',
          }}
        >
          Built for Real-World Messiness
        </motion.h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '16px',
        }}>
          {FEATURES.map(({ icon: Icon, title, desc, color }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              whileHover={{ y: -4 }}
              style={{
                ...glassCard,
                padding: '24px',
                transition: 'transform 0.2s, box-shadow 0.2s',
              }}
            >
              <div style={{
                width: '40px', height: '40px', borderRadius: '12px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: '16px',
                background: `${color}18`,
                border: `1px solid ${color}35`,
              }}>
                <Icon size={18} style={{ color }} />
              </div>
              <h3 style={{ fontWeight: 600, color: '#ffffff', marginBottom: '8px', fontSize: '15px' }}>
                {title}
              </h3>
              <p style={{ fontSize: '13px', lineHeight: 1.65, color: 'rgba(255,255,255,0.65)', margin: 0 }}>
                {desc}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
