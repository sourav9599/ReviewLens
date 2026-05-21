import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import {
  BarChart3,
  Brain,
  TrendingUp,
  FileText,
  Activity,
  Zap,
  HelpCircle,
  Globe,
  Briefcase,
  User,
  Building2,
  ChevronDown,
} from "lucide-react";
import { useReviewStore } from "../../store/reviewStore";
import clsx from "clsx";

const NAV_ITEMS = [{ to: "/dashboard", label: "Dashboard" }];

const SUB_NAV_ITEMS = [
  { to: "/dashboard", label: "ReviewLens" },
  { to: "/analyze", label: "Ingest" },
  { to: "/dashboard", label: "Analytics" },
  { to: "/review", label: "Hotel Reviews" },
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
  const [properties, setProperties] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    fetch("/api/hotel-reviews/properties")
      .then((r) => r.json())
      .then((data) => setProperties(data.properties || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div
      className="flex flex-col min-h-screen"
      style={{ background: "#F8FAFC" }}
    >
      {/* Top Header Bar */}
      <header className="bg-white border-b border-[#e0e0e0]">
        <div className="max-w-[1400px] mx-auto flex items-center justify-between h-[64px] px-6">
          {/* Logo */}
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-3"
          >
            <div className="flex flex-col items-center">
              <div
                className="text-[22px] italic text-[#1c1c1c] leading-tight"
                style={{ fontFamily: "Georgia, 'Times New Roman', serif" }}
              >
                <span className="font-normal">Review</span>
                <span className="font-bold">Lens</span>
              </div>
              <div className="text-[9px] tracking-[3px] uppercase text-[#1c1c1c] font-bold -mt-0.5">
                MARRIOTT BONVOY
              </div>
            </div>
          </button>

          {/* Main Nav */}
          <nav className="flex items-center gap-8">
            {NAV_ITEMS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  clsx(
                    "text-[13px] font-medium transition-colors",
                    isActive
                      ? "text-[#1c1c1c] underline underline-offset-[18px] decoration-2"
                      : "text-[#555] hover:text-[#1c1c1c]",
                  )
                }
              >
                {label}
              </NavLink>
            ))}

            {/* Property Selector */}
            {properties.length > 0 && (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-[#e0e0e0] hover:border-[#999] transition-colors text-[13px] font-medium text-[#333] bg-white"
                >
                  <Building2 size={14} className="text-[#555]" />
                  <span>Properties</span>
                  <ChevronDown
                    size={13}
                    className={clsx(
                      "text-[#777] transition-transform",
                      dropdownOpen && "rotate-180"
                    )}
                  />
                </button>

                {dropdownOpen && (
                  <div className="absolute top-full left-0 mt-2 w-[300px] bg-white rounded-lg shadow-lg border border-[#e5e7eb] z-50 overflow-hidden">
                    <div className="px-3 py-2 border-b border-[#f1f5f9]">
                      <p className="text-[10px] uppercase tracking-wider text-[#94a3b8] font-semibold">
                        Select Property
                      </p>
                    </div>
                    <div className="max-h-[280px] overflow-y-auto">
                      {properties.map((prop) => (
                        <button
                          key={prop.property_code}
                          onClick={() => {
                            setDropdownOpen(false);
                            navigate(`/dashboard/${prop.property_code}`);
                          }}
                          className="w-full px-3 py-2.5 text-left hover:bg-[#f8fafc] transition-colors flex items-center gap-3 border-b border-[#f8fafc] last:border-none"
                        >
                          <div className="w-8 h-8 rounded-md bg-[#f1f5f9] flex items-center justify-center flex-shrink-0">
                            <Building2 size={14} className="text-[#64748b]" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-[12px] font-medium text-[#1e293b] truncate">
                              {prop.hotel_name}
                            </p>
                            <p className="text-[10px] text-[#94a3b8]">
                              {prop.property_code} &middot; {prop.review_count} reviews
                            </p>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </nav>

          {/* Right side utilities */}
          <div className="flex items-center gap-5 text-[12px] text-[#333]">
            <button className="flex items-center gap-1 hover:text-[#1c1c1c]">
              <HelpCircle size={14} />
              Help
            </button>
            <button className="flex items-center gap-1 hover:text-[#1c1c1c]">
              <Globe size={14} />
              English
            </button>
            <button className="flex items-center gap-1 hover:text-[#1c1c1c]">
              <Briefcase size={14} />
              My Reports
            </button>
            <button className="flex items-center gap-1 hover:text-[#1c1c1c]">
              <User size={14} />
              Sign In Or Join
            </button>
          </div>
        </div>
      </header>

      {/* Sub-navigation bar */}
      {/* <div className="bg-white border-b border-[#e0e0e0]">
        <div className="max-w-[1400px] mx-auto flex items-center h-[42px] px-6 gap-8">
          {SUB_NAV_ITEMS.map(({ to, label }) => (
            <NavLink
              key={label}
              to={to}
              className={({ isActive }) =>
                clsx(
                  "text-[12px] font-medium border-b-2 h-full flex items-center transition-colors",
                  isActive && label === "ReviewLens"
                    ? "border-[#1c1c1c] text-[#1c1c1c]"
                    : "border-transparent text-[#555] hover:text-[#1c1c1c] hover:border-[#ccc]",
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div> */}

      {/* Agent Pipeline Status Bar */}
      {jobStatus === "running" && (
        <div className="bg-[#1c1c1c] text-white">
          <div className="max-w-[1400px] mx-auto flex items-center h-[36px] px-6 gap-4">
            <span className="text-[11px] font-medium tracking-wide uppercase text-white/70">
              Agent Pipeline
            </span>
            <div className="flex items-center gap-3 ml-2">
              {AGENT_PIPELINE.map(({ icon: Icon, label, color }, idx) => (
                <div key={label} className="flex items-center gap-1.5">
                  <motion.div
                    className="w-2 h-2 rounded-full"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      delay: idx * 0.25,
                    }}
                    style={{ background: color }}
                  />
                  <span className="text-[10px] text-white/80">{label}</span>
                </div>
              ))}
            </div>
            <motion.span
              className="ml-auto text-[11px] font-semibold"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              style={{ color: "#FF7A00" }}
            >
              Processing…
            </motion.span>
          </div>
        </div>
      )}

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
