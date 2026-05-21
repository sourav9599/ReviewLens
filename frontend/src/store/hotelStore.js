import { create } from "zustand";
import axios from "axios";

const API_BASE = "http://localhost:5000/api";
const HOTEL_ID = "NYCES";

export const useHotelStore = create((set, get) => ({
  reviews: [],
  loading: false,
  error: null,
  activeTab: "overview",
  selectedSentiment: null,
  searchQuery: "",
  selectedMention: null,
  mentionReviews: [],
  mentionLoading: false,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setSelectedSentiment: (s) => set({ selectedSentiment: s }),
  setSearchQuery: (q) => set({ searchQuery: q }),

  loadReviews: async () => {
    set({ loading: true, error: null });
    try {
      const { data } = await axios.get(
        `${API_BASE}/hotel-reviews/data?hotel_id=${HOTEL_ID}&page_size=500`
      );
      set({ reviews: data.reviews || [], loading: false });
    } catch (err) {
      set({ error: err.message || "Failed to load reviews", loading: false });
    }
  },

  selectMention: async (mention) => {
    set({ selectedMention: mention, mentionLoading: true });
    try {
      const { data } = await axios.get(
        `${API_BASE}/hotel-reviews/search?hotel_id=${HOTEL_ID}&tag=${encodeURIComponent(mention)}&page_size=100`
      );
      set({ mentionReviews: data.reviews || [], mentionLoading: false });
    } catch {
      set({ mentionReviews: [], mentionLoading: false });
    }
  },

  clearMention: () => set({ selectedMention: null, mentionReviews: [] }),

  getStats: () => {
    const { reviews } = get();
    if (!reviews.length) return null;

    const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
    let ratingSum = 0;
    let ratingCount = 0;

    reviews.forEach((r) => {
      if (r.sentiment && sentimentCounts[r.sentiment] !== undefined) {
        sentimentCounts[r.sentiment]++;
      }
      if (r.rating) {
        ratingSum += r.rating;
        ratingCount++;
      }
    });

    const avgRating = ratingCount > 0 ? (ratingSum / ratingCount).toFixed(1) : "N/A";
    const satisfactionRate =
      reviews.length > 0
        ? Math.round((sentimentCounts.positive / reviews.length) * 100)
        : 0;

    return {
      total: reviews.length,
      avgRating,
      satisfactionRate,
      sentimentCounts,
    };
  },

  getRatingDistribution: () => {
    const { reviews } = get();
    const dist = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    reviews.forEach((r) => {
      if (r.rating) {
        const rounded = Math.round(r.rating);
        if (dist[rounded] !== undefined) dist[rounded]++;
      }
    });
    return Object.entries(dist).map(([rating, count]) => ({
      rating: `${rating}★`,
      count,
    }));
  },

  getTopMentions: () => {
    const { reviews } = get();
    const mentionCount = {};
    reviews.forEach((r) => {
      (r.mentions || []).forEach((m) => {
        mentionCount[m] = (mentionCount[m] || 0) + 1;
      });
    });
    return Object.entries(mentionCount)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([name, count]) => ({ name, count }));
  },

  getCategoryScores: () => {
    const { reviews } = get();
    const categoryTotals = {};
    const categoryCounts = {};

    reviews.forEach((r) => {
      const subRatings = r.sub_ratings || {};
      Object.entries(subRatings).forEach(([key, val]) => {
        if (val) {
          categoryTotals[key] = (categoryTotals[key] || 0) + val;
          categoryCounts[key] = (categoryCounts[key] || 0) + 1;
        }
      });
    });

    return Object.entries(categoryTotals).map(([name, total]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      score: parseFloat((total / categoryCounts[name]).toFixed(1)),
      fullMark: 5,
    }));
  },

  getSentimentDistribution: () => {
    const { reviews } = get();
    const dist = { positive: 0, negative: 0, neutral: 0 };
    reviews.forEach((r) => {
      if (r.sentiment && dist[r.sentiment] !== undefined) {
        dist[r.sentiment]++;
      }
    });
    return Object.entries(dist).map(([name, value]) => ({ name, value }));
  },

  getFilteredReviews: () => {
    const { reviews, selectedSentiment, searchQuery } = get();
    let filtered = reviews;

    if (selectedSentiment) {
      filtered = filtered.filter((r) => r.sentiment === selectedSentiment);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          (r.text || "").toLowerCase().includes(q) ||
          (r.mentions || []).some((m) => m.toLowerCase().includes(q))
      );
    }
    return filtered;
  },

  getInsights: () => {
    const { reviews } = get();
    if (reviews.length < 3) return [];

    const insights = [];
    const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
    const mentionSentiment = {};

    reviews.forEach((r) => {
      if (r.sentiment) sentimentCounts[r.sentiment]++;
      (r.mentions || []).forEach((m) => {
        if (!mentionSentiment[m]) mentionSentiment[m] = { positive: 0, negative: 0, neutral: 0 };
        if (r.sentiment) mentionSentiment[m][r.sentiment]++;
      });
    });

    const negRate = sentimentCounts.negative / reviews.length;
    if (negRate > 0.3) {
      insights.push({
        type: "alert",
        title: "High Negative Sentiment",
        description: `${Math.round(negRate * 100)}% of reviews are negative. Immediate attention needed on guest pain points.`,
        priority: "high",
      });
    }

    if (sentimentCounts.positive / reviews.length > 0.6) {
      insights.push({
        type: "success",
        title: "Strong Guest Satisfaction",
        description: `${Math.round((sentimentCounts.positive / reviews.length) * 100)}% positive reviews indicate strong guest experience.`,
        priority: "info",
      });
    }

    Object.entries(mentionSentiment).forEach(([mention, counts]) => {
      const total = counts.positive + counts.negative + counts.neutral;
      if (total >= 3 && counts.negative / total > 0.5) {
        insights.push({
          type: "warning",
          title: `"${mention}" needs attention`,
          description: `${counts.negative} out of ${total} mentions of "${mention}" are negative. Consider operational improvements.`,
          priority: "medium",
        });
      }
    });

    Object.entries(mentionSentiment).forEach(([mention, counts]) => {
      const total = counts.positive + counts.negative + counts.neutral;
      if (total >= 3 && counts.positive / total > 0.7) {
        insights.push({
          type: "success",
          title: `"${mention}" is a strength`,
          description: `${counts.positive} out of ${total} mentions are positive. Amplify this in marketing.`,
          priority: "low",
        });
      }
    });

    return insights.slice(0, 10);
  },
}));
