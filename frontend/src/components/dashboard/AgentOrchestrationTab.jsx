import { motion, AnimatePresence } from 'framer-motion'
import { useReviewStore } from '../../store/reviewStore'
import {
  Brain, GitBranch, RefreshCw, AlertTriangle, CheckCircle2,
  ArrowRight, Cpu, Repeat, TrendingUp, Zap, Shield, Globe,
  BarChart3, FileText, Smile
} from 'lucide-react'

const AGENT_COLORS = {
  PreprocessingAgent:                '#2563EB',
  EmojiAgent:                        '#D97706',
  'OrchestratorAgent (Pre)':         '#7C3AED',
  DeduplicationAgent:                '#16A34A',
  'OrchestratorAgent (Post-Dedup)':  '#7C3AED',
  SentimentAgent:                    '#DB2777',
  'OrchestratorAgent (Post-Sentiment)': '#7C3AED',
  TrendAgent:                        '#DC2626',
  'OrchestratorAgent (Post-Trend)':  '#7C3AED',
  RecommendationAgent:               '#D97706',
  CrossComparisonAgent:              '#0891B2',
  ReportAgent:                       '#16A34A',
}

const AGENT_BG = {
  PreprocessingAgent:                '#DBEAFE',
  EmojiAgent:                        '#FEF3C7',
  'OrchestratorAgent (Pre)':         '#EDE9FE',
  DeduplicationAgent:                '#DCFCE7',
  'OrchestratorAgent (Post-Dedup)':  '#EDE9FE',
  SentimentAgent:                    '#FCE7F3',
  'OrchestratorAgent (Post-Sentiment)': '#EDE9FE',
  TrendAgent:                        '#FEE2E2',
  'OrchestratorAgent (Post-Trend)':  '#EDE9FE',
  RecommendationAgent:               '#FEF3C7',
  CrossComparisonAgent:              '#ECFEFF',
  ReportAgent:                       '#DCFCE7',
}

const AGENT_ICONS = {
  PreprocessingAgent: FileText,
  EmojiAgent: Smile,
  'OrchestratorAgent (Pre)': Brain,
  DeduplicationAgent: Shield,
  'OrchestratorAgent (Post-Dedup)': Brain,
  SentimentAgent: Zap,
  'OrchestratorAgent (Post-Sentiment)': Brain,
  TrendAgent: TrendingUp,
  'OrchestratorAgent (Post-Trend)': Brain,
  RecommendationAgent: BarChart3,
  CrossComparisonAgent: Globe,
  ReportAgent: FileText,
}

const ACTION_COLORS = {
  route:    { color: '#2563EB', bg: '#DBEAFE', border: '#BFDBFE' },
  retry:    { color: '#D97706', bg: '#FEF3C7', border: '#FDE68A' },
  skip:     { color: '#64748B', bg: '#F1F5F9', border: '#E2E8F0' },
  escalate: { color: '#DC2626', bg: '#FEE2E2', border: '#FECACA' },
}

const ACTION_ICONS = {
  route: ArrowRight,
  retry: RefreshCw,
  skip: CheckCircle2,
  escalate: AlertTriangle,
}

function AgentNode({ step, index, total }) {
  const isOrchestrator = step.agent.includes('Orchestrator')
  const color  = AGENT_COLORS[step.agent] || '#64748B'
  const bgColor = AGENT_BG[step.agent]   || '#F1F5F9'
  const Icon   = AGENT_ICONS[step.agent]  || Cpu
  const isLast = index === total - 1

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.07 }}
      className="flex items-start gap-3"
    >
      <div className="flex flex-col items-center flex-shrink-0" style={{ width: 36 }}>
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{
            background: bgColor,
            border: `1.5px solid ${color}40`,
            boxShadow: isOrchestrator ? `0 0 12px ${color}25` : 'none',
          }}
        >
          <Icon size={16} style={{ color }} />
        </div>
        {!isLast && (
          <div className="w-px flex-1 mt-1" style={{ background: '#E5E7EB', minHeight: 20 }} />
        )}
      </div>

      <div className="flex-1 pb-4">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className="text-sm font-semibold"
            style={{ color: isOrchestrator ? '#7C3AED' : '#1E293B' }}
          >
            {step.agent}
          </span>
          <span
            className="px-2 py-0.5 rounded-lg text-xs font-medium"
            style={
              step.output === 'complete'
                ? { background: '#DCFCE7', color: '#16A34A', border: '1px solid #BBF7D0' }
                : { background: '#F1F5F9', color: '#64748B', border: '1px solid #E2E8F0' }
            }
          >
            {step.output}
          </span>
        </div>

        <div className="flex flex-wrap gap-2 mt-1.5">
          {step.count > 0 && (
            <span className="text-xs" style={{ color: '#64748B' }}>
              {step.count} reviews preprocessed
            </span>
          )}
          {step.emojis > 0 && (
            <span className="text-xs font-medium" style={{ color: '#D97706' }}>
              {step.emojis} emojis · {step.reviews_with_emojis} reviews
            </span>
          )}
          {step.duplicates !== undefined && (
            <span className="text-xs" style={{ color: '#64748B' }}>
              {step.duplicates} dups · {step.bots} bots
            </span>
          )}
          {step.low_confidence > 0 && (
            <span className="text-xs font-medium" style={{ color: '#D97706' }}>
              ⚠ {step.low_confidence} low-confidence
            </span>
          )}
          {step.avg_confidence > 0 && (
            <span className="text-xs font-medium" style={{ color: '#2563EB' }}>
              avg conf: {(step.avg_confidence * 100).toFixed(0)}%
            </span>
          )}
          {step.alerts > 0 && (
            <span className="text-xs font-medium" style={{ color: '#DC2626' }}>
              {step.alerts} alerts raised
            </span>
          )}
          {step.recommendations > 0 && (
            <span className="text-xs font-medium" style={{ color: '#D97706' }}>
              {step.recommendations} recommendations
            </span>
          )}
          {step.categories > 0 && (
            <span className="text-xs font-medium" style={{ color: '#0891B2' }}>
              {step.categories} categories compared
            </span>
          )}
          {step.route && step.route !== 'proceed' && (
            <span className="text-xs px-1.5 py-0.5 rounded-lg font-medium"
              style={{ background: '#FEF3C7', color: '#D97706', border: '1px solid #FDE68A' }}>
              ↺ {step.route}
            </span>
          )}
          {step.decisions > 0 && (
            <span className="text-xs font-medium" style={{ color: '#7C3AED' }}>
              {step.decisions} decision(s)
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}

function DecisionCard({ decision, index }) {
  const ActionIcon = ACTION_ICONS[decision.action] || ArrowRight
  const style = ACTION_COLORS[decision.action] || ACTION_COLORS.route

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="rounded-xl p-4"
      style={{ background: style.bg, border: `1px solid ${style.border}` }}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ background: '#FFFFFF', border: `1px solid ${style.border}` }}
        >
          <ActionIcon size={13} style={{ color: style.color }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs font-bold px-2 py-0.5 rounded-lg"
              style={{ background: '#FFFFFF', color: style.color, border: `1px solid ${style.border}` }}>
              {decision.action.toUpperCase()}
            </span>
            <span className="text-xs font-mono" style={{ color: '#94A3B8' }}>
              [{decision.phase}]
            </span>
            <span className="text-xs font-mono" style={{ color: '#CBD5E1' }}>
              #{decision.decision_id}
            </span>
          </div>
          <div className="text-sm font-semibold mb-1" style={{ color: '#1E293B' }}>
            {decision.decision.replace(/_/g, ' ')}
          </div>
          <div className="text-xs leading-relaxed" style={{ color: '#475569' }}>
            {decision.reason}
          </div>
          {decision.affected_agents?.length > 0 && (
            <div className="flex gap-1.5 mt-2 flex-wrap">
              {decision.affected_agents.map(a => (
                <span key={a} className="text-xs px-1.5 py-0.5 rounded-lg font-medium"
                  style={{ background: '#EDE9FE', color: '#7C3AED', border: '1px solid #DDD6FE' }}>
                  → {a}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default function AgentOrchestrationTab() {
  const { getOrchestratorData } = useReviewStore()
  const { decisions, agentTrace, feedbackLoops, pipelineVersion } = getOrchestratorData()

  const statCards = [
    { label: 'Pipeline Version',      val: pipelineVersion,  color: '#2563EB', bg: '#DBEAFE', border: '#BFDBFE', sub: 'Agentic Architecture' },
    { label: 'Agents Executed',        val: agentTrace.length, color: '#16A34A', bg: '#DCFCE7', border: '#BBF7D0', sub: 'in directed graph' },
    { label: 'Orchestrator Decisions', val: decisions.length,  color: '#7C3AED', bg: '#EDE9FE', border: '#DDD6FE', sub: 'dynamic routing' },
    { label: 'Feedback Loops',         val: feedbackLoops,     color: '#D97706', bg: '#FEF3C7', border: '#FDE68A', sub: feedbackLoops > 0 ? 'triggered & resolved' : 'none required' },
  ]

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(({ label, val, color, bg, border, sub }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className="rounded-2xl p-5"
            style={{ background: bg, border: `1px solid ${border}` }}
          >
            <div className="font-bold text-3xl mb-1" style={{ color, fontFamily: 'DM Sans, sans-serif' }}>{val}</div>
            <div className="text-sm font-semibold" style={{ color: '#1E293B' }}>{label}</div>
            <div className="text-xs mt-0.5" style={{ color: '#64748B' }}>{sub}</div>
          </motion.div>
        ))}
      </div>

      {/* Feedback Loop Banner */}
      {feedbackLoops > 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          className="rounded-2xl p-4 flex items-center gap-3"
          style={{ background: '#FEF3C7', border: '1px solid #FDE68A' }}
        >
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: '#FFFFFF', border: '1px solid #FDE68A' }}>
            <Repeat size={18} style={{ color: '#D97706' }} />
          </div>
          <div>
            <div className="text-sm font-semibold" style={{ color: '#92400E' }}>
              Feedback Loop Triggered × {feedbackLoops}
            </div>
            <div className="text-xs mt-0.5 leading-relaxed" style={{ color: '#78350F' }}>
              The Orchestrator detected high bot rate and re-ran deduplication with a stricter similarity threshold.
              This is true agentic behavior — the system corrected itself without human intervention.
            </div>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Execution Trace */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="card-3d p-6"
        >
          <div className="flex items-center gap-2 mb-5">
            <GitBranch size={16} style={{ color: '#2563EB' }} />
            <h3 className="font-semibold text-base" style={{ color: '#1E293B' }}>Agent Execution Flow</h3>
          </div>
          <div>
            {agentTrace.map((step, i) => (
              <AgentNode key={i} step={step} index={i} total={agentTrace.length} />
            ))}
            {agentTrace.length === 0 && (
              <div className="text-sm text-center py-8" style={{ color: '#94A3B8' }}>
                No agent trace available
              </div>
            )}
          </div>
        </motion.div>

        {/* Orchestrator Decisions */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="card-3d p-6"
        >
          <div className="flex items-center gap-2 mb-5">
            <Brain size={16} style={{ color: '#7C3AED' }} />
            <h3 className="font-semibold text-base" style={{ color: '#1E293B' }}>Orchestrator Decision Log</h3>
            <span className="ml-auto text-xs px-2 py-0.5 rounded-lg font-semibold"
              style={{ background: '#EDE9FE', color: '#7C3AED', border: '1px solid #DDD6FE' }}>
              {decisions.length} decisions
            </span>
          </div>

          <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1"
            style={{ scrollbarWidth: 'thin', scrollbarColor: '#E5E7EB transparent' }}>
            {decisions.length === 0 && (
              <div className="text-sm text-center py-8" style={{ color: '#94A3B8' }}>
                No orchestrator decisions logged
              </div>
            )}
            {decisions.map((d, i) => (
              <DecisionCard key={d.decision_id || i} decision={d} index={i} />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Inter-Agent Communication Legend */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="card-3d p-5"
      >
        <h3 className="font-semibold text-sm mb-4" style={{ color: '#1E293B' }}>Inter-Agent Communication Bus — Event Types</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { event: 'bot_detected',  sender: 'DeduplicationAgent', color: '#DC2626', bg: '#FEE2E2', border: '#FECACA', desc: 'Emitted when review bot score exceeds threshold' },
            { event: 'low_confidence',sender: 'SentimentAgent',     color: '#D97706', bg: '#FEF3C7', border: '#FDE68A', desc: 'Triggers feedback loop evaluation by Orchestrator' },
            { event: 'emoji_found',   sender: 'EmojiAgent',         color: '#D97706', bg: '#FEF3C7', border: '#FDE68A', desc: 'Emoji signals shared for confidence boosting' },
            { event: 'quality_check', sender: 'Orchestrator',       color: '#7C3AED', bg: '#EDE9FE', border: '#DDD6FE', desc: 'Broadcast after each phase for monitoring' },
          ].map(({ event, sender, color, bg, border, desc }) => (
            <div key={event} className="rounded-xl p-3.5"
              style={{ background: bg, border: `1px solid ${border}` }}>
              <div className="text-xs font-bold font-mono mb-1" style={{ color }}>{event}</div>
              <div className="text-xs font-medium mb-1.5" style={{ color: '#64748B' }}>from: {sender}</div>
              <div className="text-xs leading-relaxed" style={{ color: '#475569' }}>{desc}</div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
