import { create } from "zustand";
import axios from "axios";

const API_BASE = "/api";

export const useReviewStore = create((set, get) => ({
  // State
  currentJob: null,
  jobStatus: null, // 'idle' | 'queued' | 'running' | 'complete' | 'failed'
  report: null,
  pollingInterval: null,
  activeTab: "overview",
  selectedCategory: "all",
  progressEvents: [],

  // Actions
  setActiveTab: (tab) => set({ activeTab: tab }),
  setSelectedCategory: (cat) => set({ selectedCategory: cat }),
  setReport: (report) => set({ report, jobStatus: "complete" }),
  setJobStatus: (status) => set({ jobStatus: status }),

  startDemoAnalysis: async () => {
    set({
      jobStatus: "queued",
      report: null,
      currentJob: null,
      progressEvents: [],
    });
    try {
      const { data } = await axios.post(`${API_BASE}/analyze/demo`);
      set({ currentJob: data.job_id });
      get().startPolling(data.job_id);
      return data;
    } catch (e) {
      set({ jobStatus: "failed" });
      throw e;
    }
  },

  startFileAnalysis: async (file, category, productName) => {
    set({
      jobStatus: "queued",
      report: null,
      currentJob: null,
      progressEvents: [],
    });
    const form = new FormData();
    form.append("file", file);
    form.append("category", category);
    form.append("product_name", productName);
    try {
      const { data } = await axios.post(`${API_BASE}/analyze/upload`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      set({ currentJob: data.job_id });
      get().startPolling(data.job_id);
      return data;
    } catch (e) {
      set({ jobStatus: "failed" });
      throw e;
    }
  },

  startPasteAnalysis: async (reviews) => {
    set({
      jobStatus: "queued",
      report: null,
      currentJob: null,
      progressEvents: [],
    });
    try {
      const { data } = await axios.post(`${API_BASE}/analyze/paste`, {
        reviews,
      });
      set({ currentJob: data.job_id });
      get().startPolling(data.job_id);
      return data;
    } catch (e) {
      set({ jobStatus: "failed" });
      throw e;
    }
  },

  startTextAnalysis: async (text, category, productName) => {
    set({
      jobStatus: "queued",
      report: null,
      currentJob: null,
      progressEvents: [],
    });
    try {
      const { data } = await axios.post(`${API_BASE}/analyze/text`, {
        text,
        category,
        product_name: productName,
      });
      set({ currentJob: data.job_id });
      get().startPolling(data.job_id);
      return data;
    } catch (e) {
      set({ jobStatus: "failed" });
      throw e;
    }
  },

  startPolling: (jobId) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get(`${API_BASE}/jobs/${jobId}`);
        set({ jobStatus: data.status });

        if (data.progress_events?.length) {
          set({ progressEvents: data.progress_events });
        }

        if (data.status === "complete") {
          clearInterval(interval);
          set({ report: data.report, pollingInterval: null });
        } else if (data.status === "failed") {
          clearInterval(interval);
          set({ pollingInterval: null });
        }
      } catch (e) {
        console.error("Polling error:", e);
      }
    }, 2500);
    set({ pollingInterval: interval });
  },

  downloadPDF: async () => {
    const { currentJob } = get();
    if (!currentJob) return;
    try {
      const response = await axios.get(`${API_BASE}/jobs/${currentJob}/pdf`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(
        new Blob([response.data], { type: "application/pdf" }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `reviewlens_report_${currentJob}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error("PDF download failed:", e);
    }
  },

  reset: () => {
    const { pollingInterval } = get();
    if (pollingInterval) clearInterval(pollingInterval);
    set({
      currentJob: null,
      jobStatus: "idle",
      report: null,
      pollingInterval: null,
      progressEvents: [],
    });
  },

  // ─── Derived Selectors ─────────────────────────────────────────────────

  getFilteredReviews: () => {
    const { report, selectedCategory } = get();
    if (!report) return [];
    const reviews = report.processed_reviews || [];
    if (selectedCategory === "all") return reviews;
    return reviews.filter((r) => r.product_category === selectedCategory);
  },

  getFeatureSummaryData: () => {
    const { report } = get();
    if (!report?.feature_summary) return [];
    return Object.entries(report.feature_summary)
      .map(([feature, data]) => ({
        feature: feature.replace(/_/g, " "),
        complaints: Math.round((data.complaint_rate || 0) * 100),
        praises: Math.round((data.praise_rate || 0) * 100),
        mentions: data.total_mentions || 0,
        confidence: Math.round((data.avg_confidence || 0) * 100),
      }))
      .filter((d) => d.mentions >= 2)
      .sort((a, b) => b.mentions - a.mentions)
      .slice(0, 12);
  },

  getTrendChartData: () => {
    const { report } = get();
    if (!report?.trend_data?.length) return [];
    const byWindow = {};
    for (const point of report.trend_data) {
      const key = point.window_index;
      if (!byWindow[key]) {
        byWindow[key] = {
          window: key,
          windowStart: point.window_start,
          windowEnd: point.window_end,
        };
      }
      byWindow[key][point.feature + "_complaints"] = Math.round(
        point.complaint_rate * 100,
      );
      byWindow[key][point.feature + "_praises"] = Math.round(
        point.praise_rate * 100,
      );
    }
    return Object.values(byWindow).sort((a, b) => a.window - b.window);
  },

  getSentimentPieData: () => {
    const { report } = get();
    if (!report?.overall_sentiment_distribution) return [];
    const colors = {
      positive: "#28C76F",
      negative: "#EA5455",
      neutral: "#FFB547",
      mixed: "#F7936F",
      sarcastic: "#A78BFA",
      ambiguous: "#60A5FA",
    };
    return Object.entries(report.overall_sentiment_distribution)
      .filter(([, v]) => v > 0)
      .map(([name, value]) => ({
        name,
        value: Math.round(value * 100),
        color: colors[name] || "#94A3B8",
      }));
  },

  getEmojiData: () => {
    const { report } = get();
    const ea = report?.emoji_analysis;
    if (!ea) return null;
    const freq = ea.emoji_frequency || {};
    const sentMap = ea.emoji_sentiment_map || {};
    const topEmojis = Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([emoji, count]) => ({
        emoji,
        count,
        sentiment: sentMap[emoji] || "neutral",
      }));
    return { ...ea, topEmojis };
  },

  getOrchestratorData: () => {
    const { report } = get();
    if (!report) return { decisions: [], messages: [], feedbackLoops: 0 };
    return {
      decisions: report.orchestrator_decisions || [],
      agentTrace: report.agent_trace || [],
      feedbackLoops: report.feedback_loops_triggered || 0,
      pipelineVersion: report.pipeline_version || "2.0",
    };
  },

  getCrossComparisonData: () => {
    const { report } = get();
    return report?.cross_product_comparison || null;
  },

  getBotRiskData: () => {
    const { report } = get();
    if (!report) return null;
    const reviews = report.processed_reviews || [];
    const riskCounts = { low: 0, medium: 0, high: 0, critical: 0 };
    reviews.forEach((r) => {
      const lvl = r.bot_risk_level || "low";
      riskCounts[lvl] = (riskCounts[lvl] || 0) + 1;
    });
    const botReviews = reviews.filter((r) => r.status === "bot_suspected");
    const topSignals = {};
    botReviews.forEach((r) => {
      (r.bot_signals || []).forEach((s) => {
        topSignals[s] = (topSignals[s] || 0) + 1;
      });
    });
    return {
      riskCounts,
      topSignals: Object.entries(topSignals)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8),
      authenticRate: Math.round(
        ((report.clean_reviews || 0) / Math.max(report.total_reviews, 1)) * 100,
      ),
      botRate: Math.round(
        ((report.bot_suspected_count || 0) /
          Math.max(report.total_reviews, 1)) *
          100,
      ),
    };
  },

  // ── NEW: Per-product satisfaction breakdown ────────────────────────────
  getProductSatisfactionData: () => {
    const { report } = get();
    if (!report) return [];
    const reviews = report.processed_reviews || [];

    // Satisfied = positive | neutral; Unsatisfied = negative | mixed | sarcastic | ambiguous
    const SATISFIED = new Set(["positive", "neutral"]);
    const UNSATISFIED = new Set([
      "negative",
      "mixed",
      "sarcastic",
      "ambiguous",
    ]);

    const byProduct = {};
    reviews.forEach((r) => {
      if (r.status === "bot_suspected" || r.status === "duplicate") return;
      const name = r.product_name || "Unknown";
      if (!byProduct[name]) {
        byProduct[name] = {
          product: name,
          satisfied: 0,
          unsatisfied: 0,
          total: 0,
          sentiments: {},
        };
      }
      const s = r.overall_sentiment || "neutral";
      byProduct[name].total++;
      byProduct[name].sentiments[s] = (byProduct[name].sentiments[s] || 0) + 1;
      if (SATISFIED.has(s)) byProduct[name].satisfied++;
      if (UNSATISFIED.has(s)) byProduct[name].unsatisfied++;
    });

    return Object.values(byProduct)
      .filter((p) => p.total >= 2)
      .map((p) => ({
        ...p,
        satisfiedRate:
          p.total > 0 ? Math.round((p.satisfied / p.total) * 100) : 0,
        unsatisfiedRate:
          p.total > 0 ? Math.round((p.unsatisfied / p.total) * 100) : 0,
      }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 8);
  },

  // ── NEW: Live feed reviews (shuffled subset for simulated feed) ─────────
  getLiveFeedReviews: () => {
    const { report } = get();
    if (!report) return [];
    const reviews = (report.processed_reviews || [])
      .filter((r) => r.cleaned_text && r.overall_sentiment)
      .slice(0, 50);
    // Fisher-Yates shuffle
    const arr = [...reviews];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr.slice(0, 30);
  },

  // ── NEW: All sentiment type counts ─────────────────────────────────────
  getSentimentTypeCounts: () => {
    const { report } = get();
    if (!report) return {};
    const reviews = (report.processed_reviews || []).filter(
      (r) => r.status !== "bot_suspected" && r.status !== "duplicate",
    );
    const counts = {
      positive: 0,
      negative: 0,
      neutral: 0,
      mixed: 0,
      sarcastic: 0,
      ambiguous: 0,
    };
    reviews.forEach((r) => {
      const s = r.overall_sentiment;
      if (s && s in counts) counts[s]++;
    });
    return counts;
  },
}));
