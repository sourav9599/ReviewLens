import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart3,
  TrendingUp,
  Zap,
  Users,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Upload,
  Shield,
  Brain,
  Smile,
  Layers,
  Download,
  Radio,
  GitBranch,
  Wifi,
  FileText,
} from "lucide-react";
import { useReviewStore } from "../store/reviewStore";
import clsx from "clsx";
import OverviewTab from "../components/dashboard/OverviewTab";
import SentimentTab from "../components/dashboard/SentimentTab";
import TrendsTab from "../components/dashboard/TrendsTab";
import RecommendationsTab from "../components/dashboard/RecommendationsTab";
import ReviewsTab from "../components/dashboard/ReviewsTab";
import AgentOrchestrationTab from "../components/dashboard/AgentOrchestrationTab";
import EmojiAnalysisTab from "../components/dashboard/EmojiAnalysisTab";
import CrossComparisonTab from "../components/dashboard/CrossComparisonTab";
import LiveFeedTicker from "../components/dashboard/LiveFeedTicker";
import AIChatAssistant from "../components/AIChatAssistant";
import ExecutiveBriefTab from "../components/dashboard/ExecutiveBriefTab";

const TABS = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "sentiment", label: "Sentiment", icon: Users },
  { id: "trends", label: "Trends", icon: TrendingUp },
  { id: "recommendations", label: "Insights", icon: Zap },
  { id: "agent_ai", label: "Agent AI", icon: Brain },
  { id: "emoji", label: "Emoji", icon: Smile },
  { id: "cross_compare", label: "Compare", icon: Layers },
  { id: "reviews", label: "All Reviews", icon: Shield },
  { id: "brief", label: "Brief", icon: FileText },
];

const PIPELINE_STAGES = [
  { key: "preprocessing", label: "Preprocessing", color: "#2563EB" },
  { key: "emoji_analysis", label: "Emoji AI", color: "#D97706" },
  { key: "orchestrator_pre", label: "Orchestrator", color: "#7C3AED" },
  { key: "deduplication", label: "Dedup + Bots", color: "#28C76F" },
  { key: "sentiment", label: "Sentiment AI", color: "#EA5455" },
  { key: "trend_detection", label: "Trends", color: "#F7936F" },
  { key: "recommendations", label: "Recommend", color: "#FF7A00" },
  { key: "cross_comparison", label: "Compare", color: "#0891B2" },
  { key: "report", label: "Report", color: "#28C76F" },
];

/* ── Loading State ────────────────────────────────────────────────────────── */
function LoadingState({ jobStatus, progressEvents }) {
  const currentStage =
    progressEvents?.length > 0
      ? progressEvents[progressEvents.length - 1]?.stage
      : null;
  const currentStageIndex = currentStage
    ? PIPELINE_STAGES.findIndex((s) => s.key === currentStage)
    : -1;

  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen gap-8 px-6"
      style={{ background: "#F8FAFC" }}
    >
      {/* Spinner */}
      <div className="relative">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
          className="w-20 h-20 rounded-full"
          style={{
            border: "3px solid #F1F5F9",
            borderTop: "3px solid #FF7A00",
            boxShadow: "0 0 30px rgba(255,122,0,0.2)",
          }}
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          className="absolute inset-3 rounded-full"
          style={{
            border: "2px solid #E5E7EB",
            borderBottom: "2px solid #28C76F",
          }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <Brain size={22} style={{ color: "#FF7A00" }} />
        </div>
      </div>

      <div className="text-center">
        <div
          className="font-bold text-2xl mb-2"
          style={{ color: "#1E293B", fontFamily: "DM Sans, sans-serif" }}
        >
          {jobStatus === "queued"
            ? "Queueing 9-Agent Pipeline…"
            : "Running Agentic Analysis…"}
        </div>
        <div className="text-sm mb-1" style={{ color: "#64748B" }}>
          Orchestrator · Emoji AI · Bot Detection · Sentiment · Trends
        </div>
        {currentStage && currentStage !== "started" && (
          <motion.div
            key={currentStage}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm mt-2 font-semibold"
            style={{ color: "#FF7A00" }}
          >
            → {progressEvents[progressEvents.length - 1]?.message}
          </motion.div>
        )}
      </div>

      {/* Stage pills */}
      <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
        {PIPELINE_STAGES.map((stage, i) => {
          const isDone = currentStageIndex > i || currentStage === "complete";
          const isActive = currentStageIndex === i;
          return (
            <motion.div
              key={stage.key}
              animate={
                isActive
                  ? { opacity: [0.6, 1, 0.6] }
                  : { opacity: isDone ? 1 : 0.35 }
              }
              transition={isActive ? { duration: 1.2, repeat: Infinity } : {}}
              className="px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5"
              style={{
                background: isDone || isActive ? `${stage.color}15` : "#F1F5F9",
                border: `1px solid ${isDone || isActive ? stage.color + "40" : "#E5E7EB"}`,
                color: isDone || isActive ? stage.color : "#94A3B8",
              }}
            >
              {isDone && <CheckCircle size={10} />}
              {isActive && <Loader2 size={10} className="animate-spin" />}
              {stage.label}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

/* ── Empty State ──────────────────────────────────────────────────────────── */
function EmptyState() {
  const navigate = useNavigate();
  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen gap-6 text-center px-8"
      style={{ background: "#F8FAFC" }}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 280, damping: 22 }}
        className="w-24 h-24 rounded-2xl flex items-center justify-center"
        style={{
          background: "#FFF3E8",
          border: "2px solid #FED7AA",
          boxShadow: "0 8px 32px rgba(255,122,0,0.18)",
        }}
      >
        <Upload size={38} style={{ color: "#FF7A00" }} />
      </motion.div>
      <div>
        <h2
          className="font-bold text-2xl mb-2"
          style={{ color: "#1E293B", fontFamily: "DM Sans, sans-serif" }}
        >
          No Analysis Yet
        </h2>
        <p className="text-sm max-w-sm" style={{ color: "#64748B" }}>
          Go to the Ingest Reviews page to upload data or run the demo dataset.
        </p>
      </div>
      <button onClick={() => navigate("/analyze")} className="btn-primary">
        Start Analysis →
      </button>
    </div>
  );
}

/* ── Main Dashboard ───────────────────────────────────────────────────────── */
export default function DashboardPage() {
  const {
    report,
    jobStatus,
    activeTab,
    setActiveTab,
    progressEvents,
    downloadPDF,
    currentJob,
  } = useReviewStore();
  const [liveFeedOpen, setLiveFeedOpen] = useState(false);
  const isLoading = jobStatus === "running" || jobStatus === "queued";

  if (isLoading)
    return (
      <LoadingState jobStatus={jobStatus} progressEvents={progressEvents} />
    );
  if (!report) return <EmptyState />;

  const tabContent = {
    overview: <OverviewTab />,
    sentiment: <SentimentTab />,
    trends: <TrendsTab />,
    recommendations: <RecommendationsTab />,
    agent_ai: <AgentOrchestrationTab />,
    emoji: <EmojiAnalysisTab />,
    cross_compare: <CrossComparisonTab />,
    reviews: <ReviewsTab />,
    brief: <ExecutiveBriefTab />,
  };

  return (
    <div className="min-h-screen" style={{ background: "#F8FAFC" }}>
      {/* ── Sticky Header ── */}
      <div
        className="sticky top-0 z-20 px-6 pt-4 pb-0"
        style={{
          background: "rgba(248,250,252,0.95)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid #E5E7EB",
          boxShadow: "0 1px 8px rgba(0,0,0,0.06)",
        }}
      >
        {/* ── Title + actions row ── */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <motion.h1
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              className="font-bold text-2xl"
              style={{ color: "#1E293B", fontFamily: "DM Sans, sans-serif" }}
            >
              Intelligence Dashboard
            </motion.h1>
            {/* Meta row */}
            <div className="flex items-center gap-3 mt-1 flex-wrap">
              <span className="text-xs" style={{ color: "#94A3B8" }}>
                ID:{" "}
                <span
                  className="font-mono font-semibold"
                  style={{ color: "#FF7A00" }}
                >
                  {report.report_id}
                </span>
              </span>
              <span style={{ color: "#CBD5E1" }}>·</span>
              <span
                className="text-xs font-semibold"
                style={{ color: "#28C76F" }}
              >
                ⚡ {report.processing_time_seconds}s
              </span>
              <span style={{ color: "#CBD5E1" }}>·</span>
              <span
                className="text-xs px-2 py-0.5 rounded-full font-semibold"
                style={{
                  background: "#EDE9FE",
                  color: "#7C3AED",
                  border: "1px solid #DDD6FE",
                }}
              >
                v{report.pipeline_version || "2.0"}
              </span>
              {report.feedback_loops_triggered > 0 && (
                <>
                  <span style={{ color: "#CBD5E1" }}>·</span>
                  <span
                    className="text-xs font-semibold"
                    style={{ color: "#D97706" }}
                  >
                    ↺ {report.feedback_loops_triggered} feedback loop(s)
                  </span>
                </>
              )}
              {report.trend_alerts?.some((a) => a.severity === "critical") && (
                <>
                  <span style={{ color: "#CBD5E1" }}>·</span>
                  <motion.span
                    animate={{ opacity: [0.7, 1, 0.7] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="flex items-center gap-1 text-xs font-semibold"
                    style={{ color: "#DC2626" }}
                  >
                    <AlertTriangle size={11} />
                    {
                      report.trend_alerts.filter(
                        (a) => a.severity === "critical",
                      ).length
                    }{" "}
                    critical
                  </motion.span>
                </>
              )}
            </div>
          </div>

          {/* Right: stats + buttons */}
          <div className="flex items-center gap-3">
            {/* Quick stats */}
            {[
              {
                val: report.total_reviews,
                label: "Total",
                color: "#2563EB",
                bg: "#DBEAFE",
              },
              {
                val: report.clean_reviews,
                label: "Clean",
                color: "#28C76F",
                bg: "#DCFCE7",
              },
              {
                val: report.bot_suspected_count,
                label: "Bots",
                color: "#EA5455",
                bg: "#FEE2E2",
              },
              {
                val: report.trend_alerts?.length || 0,
                label: "Alerts",
                color: "#D97706",
                bg: "#FEF3C7",
              },
            ].map(({ val, label, color, bg }) => (
              <div
                key={label}
                className="text-center px-3 py-2 rounded-xl hidden lg:block"
                style={{ background: bg, border: `1px solid ${color}30` }}
              >
                <div
                  className="font-bold text-lg leading-none"
                  style={{ color, fontFamily: "DM Sans, sans-serif" }}
                >
                  {val}
                </div>
                <div
                  className="text-xs mt-0.5 font-medium"
                  style={{ color: "#64748B" }}
                >
                  {label}
                </div>
              </div>
            ))}

            {/* Live Feed toggle */}
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => setLiveFeedOpen((v) => !v)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition-all"
              style={{
                background: liveFeedOpen ? "#FFF3E8" : "#FFFFFF",
                borderColor: liveFeedOpen ? "#FED7AA" : "#E5E7EB",
                color: liveFeedOpen ? "#FF7A00" : "#64748B",
                boxShadow: liveFeedOpen
                  ? "0 0 0 3px rgba(255,122,0,0.1)"
                  : "none",
              }}
              title="Toggle Live Review Feed"
            >
              <Radio size={13} />
              <span className="hidden sm:inline">Live Feed</span>
              {liveFeedOpen && (
                <motion.span
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="w-1.5 h-1.5 rounded-full bg-green-400"
                />
              )}
            </motion.button>

            {/* PDF Download */}
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={downloadPDF}
              className="btn-primary"
              title="Download PDF Report"
            >
              <Download size={14} />
              <span className="hidden sm:inline">Export PDF</span>
            </motion.button>
          </div>
        </div>

        {/* ── Tab Bar ── */}
        <div
          className="flex gap-1 overflow-x-auto pb-0"
          style={{ scrollbarWidth: "none" }}
        >
          {TABS.map(({ id, label, icon: Icon }) => {
            const isActive = activeTab === id;
            return (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className="flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold transition-all whitespace-nowrap relative"
                style={{
                  color: isActive ? "#FF7A00" : "#64748B",
                  borderBottom: isActive
                    ? "2px solid #FF7A00"
                    : "2px solid transparent",
                  background: "transparent",
                }}
              >
                <Icon size={13} />
                {label}
                {id === "trends" &&
                  report.trend_alerts?.some(
                    (a) => a.severity === "critical",
                  ) && (
                    <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-red-500" />
                  )}
                {id === "agent_ai" && report.feedback_loops_triggered > 0 && (
                  <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-yellow-500" />
                )}
                {id === "emoji" &&
                  (report.emoji_analysis?.total_emojis_found || 0) > 0 && (
                    <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-orange-400" />
                  )}
                {id === "cross_compare" &&
                  report.cross_product_comparison?.categories?.length > 1 && (
                    <span className="w-1.5 h-1.5 rounded-full flex-shrink-0 bg-blue-400" />
                  )}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Tab Content ── */}
      <div className="p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            id={`dashboard-section-${activeTab}`}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            {tabContent[activeTab]}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* ── Live Feed Ticker ── */}
      <AnimatePresence>
        {liveFeedOpen && (
          <LiveFeedTicker
            isOpen={liveFeedOpen}
            onToggle={() => setLiveFeedOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* ── AI Chat Assistant (floating, dashboard-aware) ── */}
      <AIChatAssistant />
    </div>
  );
}
