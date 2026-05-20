import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  BarChart3,
  Upload,
  Brain,
  TrendingUp,
  FileText,
  Activity,
  Zap,
  Hotel,
} from "lucide-react";
import { useReviewStore } from "../../store/reviewStore";
import clsx from "clsx";

const NAV_ITEMS = [
  { to: "/analyze", icon: Upload, label: "Ingest Reviews" },
  { to: "/dashboard", icon: BarChart3, label: "Dashboard" },
  { to: "/hotelDashboard", icon: Hotel, label: "Hotel Dashboard" },
];

const AGENT_PIPELINE = [
  { icon: FileText, label: "Preprocessing", color: "#2563EB", bg: "#DBEAFE" },
  { icon: Activity, label: "Deduplication", color: "#7C3AED", bg: "#EDE9FE" },
  { icon: Brain, label: "Sentiment AI", color: "#28C76F", bg: "#DCFCE7" },
  { icon: TrendingUp, label: "Trend Detect", color: "#D97706", bg: "#FEF3C7" },
  { icon: Zap, label: "Recommend", color: "#FF7A00", bg: "#FFF3E8" },
  { icon: BarChart3, label: "Report Agent", color: "#0891B2", bg: "#ECFEFF" },
];

export default function Layout() {
  const navigate = useNavigate();
  const { jobStatus } = useReviewStore();

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ background: "#F8FAFC" }}
    >
      {/* ── Sidebar ────────────────────────────────────────────────── */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-64 flex-shrink-0 flex flex-col border-r"
        style={{
          borderColor: "#E5E7EB",
          background: "#FFFFFF",
          boxShadow: "2px 0 12px rgba(0,0,0,0.04)",
        }}
      >
        {/* Logo */}
        <div className="p-6 border-b" style={{ borderColor: "#E5E7EB" }}>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-3 group"
          >
            <div
              className="relative w-10 h-10 rounded-xl flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, #FFF3E8, #FFF8F2)",
                border: "1.5px solid #FED7AA",
                boxShadow: "0 4px 14px rgba(255,122,0,0.2)",
              }}
            >
              <Brain size={19} style={{ color: "#FF7A00" }} />
            </div>
            <div>
              <div
                className="font-bold text-lg leading-none"
                style={{ color: "#1E293B", fontFamily: "DM Sans, sans-serif" }}
              >
                ReviewLens
              </div>
              <div
                className="text-xs mt-0.5 font-medium"
                style={{ color: "#94A3B8" }}
              >
                Intelligence Platform
              </div>
            </div>
          </button>
        </div>

        {/* Nav */}
        <nav className="p-4 flex flex-col gap-1">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to}>
              {({ isActive }) => (
                <motion.div
                  whileHover={{ x: 3 }}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all"
                  style={
                    isActive
                      ? {
                          background:
                            "linear-gradient(135deg, #FFF3E8, #FFF8F2)",
                          border: "1px solid #FED7AA",
                          color: "#FF7A00",
                          boxShadow: "0 2px 8px rgba(255,122,0,0.12)",
                        }
                      : {
                          color: "#64748B",
                          border: "1px solid transparent",
                        }
                  }
                >
                  <Icon
                    size={16}
                    style={{ color: isActive ? "#FF7A00" : "#94A3B8" }}
                  />
                  {label}
                  {isActive && (
                    <motion.div
                      layoutId="active-nav"
                      className="ml-auto w-2 h-2 rounded-full"
                      style={{ background: "#FF7A00" }}
                    />
                  )}
                </motion.div>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Agent Pipeline Status */}
        <div
          className="p-4 mt-auto border-t"
          style={{ borderColor: "#E5E7EB" }}
        >
          <div
            className="text-xs font-bold uppercase tracking-wider mb-3"
            style={{ color: "#CBD5E1" }}
          >
            Agent Pipeline
          </div>
          <div className="flex flex-col gap-2">
            {AGENT_PIPELINE.map(({ icon: Icon, label, color, bg }, idx) => (
              <div key={label} className="flex items-center gap-2.5">
                <div
                  className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: bg, border: `1px solid ${color}30` }}
                >
                  <Icon size={11} style={{ color }} />
                </div>
                <span
                  className="text-xs font-medium"
                  style={{ color: "#94A3B8" }}
                >
                  {label}
                </span>
                {jobStatus === "running" && (
                  <motion.div
                    className="ml-auto w-1.5 h-1.5 rounded-full"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      delay: idx * 0.25,
                    }}
                    style={{ background: color }}
                  />
                )}
              </div>
            ))}
          </div>

          {jobStatus === "running" && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 px-3 py-2 rounded-xl text-xs text-center font-semibold"
              style={{
                background: "#FFF3E8",
                border: "1px solid #FED7AA",
                color: "#FF7A00",
              }}
            >
              ⚡ Processing…
            </motion.div>
          )}
        </div>
      </motion.aside>

      {/* Main content */}
      <main
        className="flex-1 overflow-y-auto"
        style={{ background: "#F8FAFC" }}
      >
        <Outlet />
      </main>
    </div>
  );
}
