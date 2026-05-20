/**
 * AIChatAssistant.jsx
 * Floating AI chat panel — appears only when dashboard data is loaded.
 * Sends user queries + dashboard context to POST /chat,
 * renders the answer and clickable keyword chips that scroll/highlight
 * the relevant dashboard section.
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageCircle,
  X,
  Send,
  Loader2,
  Bot,
  User,
  AlertCircle,
} from "lucide-react";
import { useReviewStore } from "../store/reviewStore";

/* ─── Section ID mapping ────────────────────────────────────────────────────
   Maps keyword tokens → DOM element IDs that exist in the dashboard tabs.
   The mapping is intentionally broad; any keyword that partially matches a
   key will resolve to the section id.  New sections can be added here.
─────────────────────────────────────────────────────────────────────────── */
const KEYWORD_SECTION_MAP = [
  {
    patterns: [
      "sentiment",
      "emotion",
      "mood",
      "feeling",
      "positive",
      "negative",
      "neutral",
      "mixed",
      "sarcastic",
    ],
    section: "sentiment",
    tabId: "sentiment",
  },
  {
    patterns: [
      "trend",
      "alert",
      "spike",
      "anomaly",
      "change",
      "detection",
      "surge",
    ],
    section: "trends",
    tabId: "trends",
  },
  {
    patterns: [
      "recommend",
      "insight",
      "action",
      "suggestion",
      "improve",
      "priority",
    ],
    section: "recommendations",
    tabId: "recommendations",
  },
  {
    patterns: [
      "overview",
      "summary",
      "total",
      "clean",
      "duplicate",
      "bot",
      "report",
    ],
    section: "overview",
    tabId: "overview",
  },
  { patterns: ["emoji", "emoticon"], section: "emoji", tabId: "emoji" },
  {
    patterns: ["compare", "comparison", "cross", "product", "category"],
    section: "cross_compare",
    tabId: "cross_compare",
  },
  {
    patterns: [
      "agent",
      "pipeline",
      "orchestrat",
      "stage",
      "processing",
      "loop",
      "feedback",
    ],
    section: "agent_ai",
    tabId: "agent_ai",
  },
  {
    patterns: ["review", "text", "raw", "comment", "all review"],
    section: "reviews",
    tabId: "reviews",
  },
  // feature-level patterns — map to the sentiment/overview tabs where charts live
  {
    patterns: ["battery", "charge", "charging"],
    section: "sentiment",
    tabId: "sentiment",
  },
  {
    patterns: ["delivery", "shipping", "package"],
    section: "overview",
    tabId: "overview",
  },
  {
    patterns: ["price", "cost", "value", "expensive"],
    section: "sentiment",
    tabId: "sentiment",
  },
  {
    patterns: ["quality", "build", "material"],
    section: "overview",
    tabId: "overview",
  },
  {
    patterns: ["sound", "audio", "noise", "volume"],
    section: "sentiment",
    tabId: "sentiment",
  },
  {
    patterns: ["design", "look", "aesthetic"],
    section: "overview",
    tabId: "overview",
  },
  {
    patterns: ["performance", "speed", "fast", "slow"],
    section: "trends",
    tabId: "trends",
  },
  {
    patterns: ["customer", "support", "service"],
    section: "recommendations",
    tabId: "recommendations",
  },
];

function resolveKeyword(keyword) {
  const lower = keyword.toLowerCase();
  for (const entry of KEYWORD_SECTION_MAP) {
    if (entry.patterns.some((p) => lower.includes(p) || p.includes(lower))) {
      return { section: entry.section, tabId: entry.tabId };
    }
  }
  return null;
}

/* ─── Highlight animation ───────────────────────────────────────────────── */
function highlightSection(sectionId) {
  const el = document.getElementById(`dashboard-section-${sectionId}`);
  if (!el) return;

  el.scrollIntoView({ behavior: "smooth", block: "center" });

  // Remove any previous highlight class
  el.classList.remove("ai-highlight");
  // Force reflow so re-adding triggers animation
  void el.offsetWidth;
  el.classList.add("ai-highlight");

  setTimeout(() => el.classList.remove("ai-highlight"), 2000);
}

/* ─── Build dashboard context payload ──────────────────────────────────── */
function buildContext(report) {
  if (!report) return {};
  return {
    total_reviews: report.total_reviews,
    clean_reviews: report.clean_reviews,
    duplicate_count: report.duplicate_count,
    bot_suspected_count: report.bot_suspected_count,
    overall_sentiment_distribution: report.overall_sentiment_distribution,
    feature_sentiment: report.feature_sentiment,
    trend_alerts: report.trend_alerts?.slice(0, 10),
    recommendations: report.recommendations?.slice(0, 8),
    product_categories: report.product_categories,
    processing_time_seconds: report.processing_time_seconds,
    feedback_loops_triggered: report.feedback_loops_triggered,
    top_complaints: report.top_complaints?.slice(0, 5),
    top_praises: report.top_praises?.slice(0, 5),
    emoji_analysis: report.emoji_analysis
      ? {
          total_emojis_found: report.emoji_analysis.total_emojis_found,
          sentiment_via_emojis: report.emoji_analysis.sentiment_via_emojis,
        }
      : null,
    cross_product_comparison: report.cross_product_comparison
      ? {
          categories: report.cross_product_comparison.categories,
          winner: report.cross_product_comparison.winner,
        }
      : null,
  };
}

/* ─── Single message bubble ─────────────────────────────────────────────── */
function MessageBubble({ msg, onKeywordClick }) {
  const isUser = msg.role === "user";
  const isError = msg.role === "error";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className={`flex gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mt-0.5"
        style={{
          background: isUser ? "#FF7A00" : isError ? "#EA5455" : "#1E293B",
          border: `1px solid ${isUser ? "#E66E00" : isError ? "#DC2626" : "#334155"}`,
        }}
      >
        {isUser ? (
          <User size={11} color="#fff" />
        ) : isError ? (
          <AlertCircle size={11} color="#fff" />
        ) : (
          <Bot size={11} color="#FF7A00" />
        )}
      </div>

      <div className="flex flex-col gap-1.5 max-w-[82%]">
        {/* Bubble */}
        <div
          className="rounded-2xl px-3 py-2 text-xs leading-relaxed"
          style={{
            background: isUser
              ? "linear-gradient(135deg, #FF7A00, #E66E00)"
              : isError
                ? "#2D1B1B"
                : "#1E293B",
            color: isUser ? "#fff" : isError ? "#FCA5A5" : "#E2E8F0",
            border: `1px solid ${isUser ? "#FF7A00" : isError ? "#7F1D1D" : "#334155"}`,
            borderBottomRightRadius: isUser ? "4px" : "16px",
            borderBottomLeftRadius: isUser ? "16px" : "4px",
          }}
        >
          {msg.text}
        </div>

        {/* Keyword chips */}
        {msg.keywords?.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {msg.keywords.map((kw) => {
              const resolved = resolveKeyword(kw);
              return (
                <button
                  key={kw}
                  onClick={() =>
                    resolved && onKeywordClick(resolved.section, resolved.tabId)
                  }
                  className="px-2 py-0.5 rounded-full text-xs font-semibold transition-all"
                  style={{
                    background: resolved ? "#FF7A0022" : "#33415520",
                    border: `1px solid ${resolved ? "#FF7A0055" : "#33415540"}`,
                    color: resolved ? "#FF7A00" : "#64748B",
                    cursor: resolved ? "pointer" : "default",
                  }}
                  title={resolved ? `Jump to ${resolved.section}` : kw}
                >
                  # {kw}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
}

/* ─── Main Component ────────────────────────────────────────────────────── */
export default function AIChatAssistant() {
  const { report, setActiveTab } = useReviewStore();

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I'm ReviewLens Assistant. Ask me anything about the current dashboard data — sentiment, trends, recommendations, or specific features.",
      keywords: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  // Focus input when panel opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open]);

  // Don't render if no report
  if (!report) return null;

  const handleKeywordClick = useCallback(
    (sectionId, tabId) => {
      // Switch to the correct tab first
      setActiveTab(tabId);
      // Give React time to render the tab, then highlight
      setTimeout(() => highlightSection(sectionId), 350);
    },
    [setActiveTab],
  );

  const sendMessage = async () => {
    const query = input.trim();
    if (!query || loading) return;

    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", text: query, keywords: [] },
    ]);
    setLoading(true);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, context: buildContext(report) }),
      });

      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer || "No answer returned.",
          keywords: Array.isArray(data.keywords) ? data.keywords : [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "error",
          text: "Could not reach the chat service. Make sure the backend is running.",
          keywords: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* ── Floating Button ── */}
      <AnimatePresence>
        {!open && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.94 }}
            onClick={() => setOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-xl"
            style={{
              background: "linear-gradient(135deg, #FF7A00, #E66E00)",
              boxShadow:
                "0 8px 32px rgba(255,122,0,0.45), 0 2px 8px rgba(0,0,0,0.2)",
            }}
            aria-label="Open AI Chat Assistant"
          >
            <MessageCircle size={24} color="#fff" />
            {/* Pulse ring */}
            <motion.span
              className="absolute inset-0 rounded-full"
              animate={{ scale: [1, 1.4], opacity: [0.4, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ border: "2px solid #FF7A00" }}
            />
          </motion.button>
        )}
      </AnimatePresence>

      {/* ── Chat Panel ── */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.88, y: 24, originX: 1, originY: 1 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.88, y: 24 }}
            transition={{ type: "spring", stiffness: 340, damping: 28 }}
            className="fixed bottom-6 right-6 z-50 flex flex-col rounded-2xl overflow-hidden"
            style={{
              width: "340px",
              height: "460px",
              background: "#0F172A",
              border: "1px solid #1E293B",
              boxShadow:
                "0 24px 64px rgba(0,0,0,0.5), 0 4px 16px rgba(255,122,0,0.1)",
            }}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-4 py-3 flex-shrink-0"
              style={{
                background: "linear-gradient(135deg, #1E293B, #0F172A)",
                borderBottom: "1px solid #1E293B",
              }}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-xl flex items-center justify-center"
                  style={{
                    background: "linear-gradient(135deg, #FF7A00, #E66E00)",
                  }}
                >
                  <Bot size={15} color="#fff" />
                </div>
                <div>
                  <div
                    className="text-xs font-bold"
                    style={{
                      color: "#F1F5F9",
                      fontFamily: "DM Sans, sans-serif",
                    }}
                  >
                    ReviewLens Assistant
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                    <span className="text-xs" style={{ color: "#64748B" }}>
                      Dashboard-aware
                    </span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="w-7 h-7 rounded-lg flex items-center justify-center transition-all hover:bg-slate-700"
                style={{ color: "#64748B" }}
                aria-label="Close"
              >
                <X size={15} />
              </button>
            </div>

            {/* Messages */}
            <div
              ref={scrollRef}
              className="flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-3"
              style={{
                scrollbarWidth: "thin",
                scrollbarColor: "#1E293B transparent",
              }}
            >
              {messages.map((msg, i) => (
                <MessageBubble
                  key={i}
                  msg={msg}
                  onKeywordClick={handleKeywordClick}
                />
              ))}

              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-2 items-center"
                >
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
                    style={{
                      background: "#1E293B",
                      border: "1px solid #334155",
                    }}
                  >
                    <Bot size={11} color="#FF7A00" />
                  </div>
                  <div
                    className="rounded-2xl px-3 py-2.5 flex items-center gap-1.5"
                    style={{
                      background: "#1E293B",
                      border: "1px solid #334155",
                    }}
                  >
                    {[0, 1, 2].map((i) => (
                      <motion.span
                        key={i}
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ background: "#FF7A00" }}
                        animate={{ opacity: [0.3, 1, 0.3], y: [0, -3, 0] }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          delay: i * 0.2,
                        }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </div>

            {/* Suggested prompts (shown before first user message) */}
            {messages.length === 1 && (
              <div
                className="px-3 pb-2 flex flex-wrap gap-1.5"
                style={{ borderTop: "1px solid #1E293B" }}
              >
                {[
                  "What is the biggest issue?",
                  "Summarize sentiment",
                  "Show critical alerts",
                  "Top recommendations",
                ].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => {
                      setInput(prompt);
                      setTimeout(() => inputRef.current?.focus(), 50);
                    }}
                    className="px-2 py-1 rounded-full text-xs font-medium transition-all hover:opacity-80"
                    style={{
                      background: "#1E293B",
                      border: "1px solid #334155",
                      color: "#94A3B8",
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}

            {/* Input row */}
            <div
              className="flex items-center gap-2 px-3 py-2.5 flex-shrink-0"
              style={{ borderTop: "1px solid #1E293B", background: "#0F172A" }}
            >
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about the dashboard…"
                disabled={loading}
                className="flex-1 text-xs rounded-xl px-3 py-2.5 outline-none transition-all"
                style={{
                  background: "#1E293B",
                  border: "1px solid #334155",
                  color: "#E2E8F0",
                  caretColor: "#FF7A00",
                }}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || loading}
                className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all"
                style={{
                  background:
                    !input.trim() || loading
                      ? "#1E293B"
                      : "linear-gradient(135deg, #FF7A00, #E66E00)",
                  border: "1px solid #334155",
                  color: !input.trim() || loading ? "#475569" : "#fff",
                  cursor: !input.trim() || loading ? "not-allowed" : "pointer",
                }}
                aria-label="Send"
              >
                {loading ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Send size={14} />
                )}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
