import React, { useState, useEffect } from "react";
import axios from "axios";

function FilledCircle({ color = "#8B6914" }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14">
      <circle cx="7" cy="7" r="6" fill={color} stroke={color} strokeWidth="1" />
    </svg>
  );
}

function EmptyCircle({ color = "#8B6914" }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14">
      <circle cx="7" cy="7" r="6" fill="none" stroke={color} strokeWidth="1" />
    </svg>
  );
}

function HalfCircle({ color = "#8B6914" }) {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14">
      <defs>
        <clipPath id="halfClip">
          <rect x="0" y="0" width="7" height="14" />
        </clipPath>
      </defs>
      <circle cx="7" cy="7" r="6" fill="none" stroke={color} strokeWidth="1" />
      <circle cx="7" cy="7" r="6" fill={color} clipPath="url(#halfClip)" />
    </svg>
  );
}

function RatingDots({ rating, max = 5 }) {
  const dots = [];
  for (let i = 1; i <= max; i++) {
    if (i <= Math.floor(rating)) {
      dots.push(<FilledCircle key={i} />);
    } else if (i === Math.ceil(rating) && rating % 1 >= 0.5) {
      dots.push(<HalfCircle key={i} />);
    } else {
      dots.push(<EmptyCircle key={i} />);
    }
  }
  return <span className="inline-flex items-center gap-[2px]">{dots}</span>;
}

function RatingBar({ label, value, maxWidth = 80, color = "#8B6914" }) {
  const percentage = (value / 5) * 100;
  return (
    <div className="flex items-center gap-2 text-[11px]">
      <span className="w-[100px] text-right text-[#333]">{label}</span>
      <div className="w-[80px] h-[10px] bg-[#e8e8e8] relative">
        <div
          className="h-full absolute left-0 top-0"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export default function ReviewPage() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("/api/hotel-reviews/NYCES/summary?force_refresh=false")
      .then((res) => {
        setSummary(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const subRatings = summary?.sub_ratings_avg || {};
  const ratingLabels = {
    cleanliness: "Cleanliness",
    location: "Location",
    amenities: "Amenities",
    dining: "Dining",
    service: "Service & Staff",
    value: "Value for Money",
  };

  return (
    <div
      className="min-h-screen bg-white"
      // style={{
      //   fontFamily:
      //     "'Swiss 721', 'Swis721 BT', 'Helvetica Neue', Helvetica, Arial, sans-serif",
      // }}
    >
      {/* Top black bar */}
      <div className="bg-[#1c1c1c] h-[40px] flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <button className="text-white">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect y="3" width="20" height="2" fill="white" />
              <rect y="9" width="20" height="2" fill="white" />
              <rect y="15" width="20" height="2" fill="white" />
            </svg>
          </button>
        </div>
        <div className="flex items-center gap-4">
          <button className="flex items-center gap-1.5 text-white text-[12px] border border-white/40 rounded px-3 py-1">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <circle cx="6" cy="4" r="3" stroke="white" strokeWidth="1" />
              <path
                d="M1 11c0-2.5 2.2-4 5-4s5 1.5 5 4"
                stroke="white"
                strokeWidth="1"
              />
            </svg>
            Sign in or Join
          </button>
          <div className="text-white text-[11px] font-bold tracking-wider">
            MARRIOTT
            <br />
            <span className="text-[10px] font-light tracking-[3px]">
              BONVOY
            </span>
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <div className="border-b border-[#e0e0e0] bg-white">
        <div className="max-w-[90vw] mx-auto flex items-center justify-between h-[60px] px-4">
          <div className="flex items-center">
            <div style={{ fontFamily: "serif" }}>
              <div
                className="text-[22px] tracking-[4px] font-light text-[#1c1c1c]"
                style={{ letterSpacing: "5px" }}
              >
                COURTYARD
              </div>
              <div className="text-[9px] tracking-[1.5px] text-[#666] -mt-1">
                by Marriott
              </div>
            </div>
          </div>
          <nav className="flex items-center gap-8 text-[13px] text-[#333]">
            <a href="#" className="hover:underline">
              Overview
            </a>
            <a href="#" className="hover:underline">
              Gallery
            </a>
            <a href="#" className="hover:underline">
              Accommodations
            </a>
            <a href="#" className="hover:underline">
              Experiences
            </a>
          </nav>
        </div>
      </div>

      {/* Hotel name bar */}
      <div className="border-b border-[#e0e0e0]">
        <div className="max-w-[90vw] mx-auto flex items-center justify-between h-[50px] px-4">
          <div className="flex items-center gap-3">
            <h1 className="text-[15px] font-normal text-[#1c1c1c]">
              {summary?.hotel_name ||
                "Courtyard by Marriott New York Manhattan/Fifth Avenue"}
            </h1>
            <span className="inline-flex items-center gap-1">
              <RatingDots rating={3.8} />
              <span className="text-[13px] text-[#333] ml-1">3.8</span>
            </span>
            <span className="text-[13px] text-[#333]">•</span>
            <a href="#" className="text-[13px] text-[#333] underline">
              {summary?.total_reviews_summarized || 1746} Reviews
            </a>
          </div>
          <div className="flex items-center gap-6 text-[12px] text-[#333]">
            <span className="flex items-center gap-1">
              <svg width="12" height="14" viewBox="0 0 12 14" fill="none">
                <path
                  d="M6 0C3 0 0 2.5 0 6c0 4 6 8 6 8s6-4 6-8c0-3.5-3-6-6-6zm0 8a2 2 0 110-4 2 2 0 010 4z"
                  fill="#1c1c1c"
                />
              </svg>
              VIEW MAP
            </span>
            <span className="flex items-center gap-1">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path
                  d="M11 8.5v2a1 1 0 01-1 1H2a1 1 0 01-1-1v-2M3.5 3L6 .5 8.5 3M6 .5v8"
                  stroke="#1c1c1c"
                  strokeWidth="1"
                />
              </svg>
              +1 212-447-1500
            </span>
          </div>
        </div>
      </div>

      {/* Date picker / Rooms / Rate bar */}
      <div className="border-b border-[#e0e0e0]">
        <div className="max-w-[90vw] mx-auto flex items-center h-[70px] px-4">
          <div className="flex-1 flex items-center gap-4 border-r border-[#e0e0e0] pr-6">
            <div>
              <div className="text-[10px] text-[#666] uppercase tracking-wide flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <rect
                    x="1"
                    y="2"
                    width="10"
                    height="9"
                    rx="1"
                    stroke="#666"
                    strokeWidth="0.8"
                  />
                  <line
                    x1="1"
                    y1="5"
                    x2="11"
                    y2="5"
                    stroke="#666"
                    strokeWidth="0.8"
                  />
                  <line
                    x1="4"
                    y1="0.5"
                    x2="4"
                    y2="3"
                    stroke="#666"
                    strokeWidth="0.8"
                  />
                  <line
                    x1="8"
                    y1="0.5"
                    x2="8"
                    y2="3"
                    stroke="#666"
                    strokeWidth="0.8"
                  />
                </svg>
                DATES (1 NIGHT)
              </div>
              <div className="text-[13px] text-[#1c1c1c] mt-1 flex items-center gap-3">
                <span>Sun, May 17</span>
                <span className="text-[#999]">→</span>
                <span>Mon, May 18</span>
              </div>
            </div>
          </div>
          <div className="flex-1 flex items-center gap-4 border-r border-[#e0e0e0] px-6">
            <div>
              <div className="text-[10px] text-[#666] uppercase tracking-wide">
                ROOMS & GUESTS
              </div>
              <div className="text-[13px] text-[#1c1c1c] mt-1 flex items-center gap-2">
                1 Room, 1 Adult
                <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                  <path d="M1 1l4 4 4-4" stroke="#333" strokeWidth="1.2" />
                </svg>
              </div>
            </div>
          </div>
          <div className="flex-1 flex items-center gap-4 px-6">
            <div>
              <div className="text-[10px] text-[#666] uppercase tracking-wide">
                SPECIAL RATES
              </div>
              <div className="text-[13px] text-[#1c1c1c] mt-1 flex items-center gap-2">
                Lowest Regular Rate
                <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                  <path d="M1 1l4 4 4-4" stroke="#333" strokeWidth="1.2" />
                </svg>
              </div>
            </div>
          </div>
          <button className="bg-[#1c1c1c] text-white text-[13px] font-medium px-6 py-2.5 rounded">
            View Rates
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-[90vw] mx-auto px-4 py-10">
        {/* GUEST REVIEWS heading */}
        <h2
          className="text-[28px] font-light text-[#1c1c1c] tracking-wide uppercase"
          style={{ fontFamily: "serif" }}
        >
          Guest Reviews
        </h2>
        <p className="text-[13px] text-[#555] mt-2 mb-8">
          Read what guests had to say on their online satisfaction survey,
          completed after a confirmed stay
        </p>

        {/* Reviews Summary Box */}
        <div className="border border-[#d0d0d0] rounded p-5 mb-8">
          {loading ? (
            <div className="text-[13px] text-[#666] py-4">
              Loading summary...
            </div>
          ) : error ? (
            <div className="text-[13px] text-[#c0392b] py-4">
              Failed to load summary: {error}
            </div>
          ) : summary ? (
            <div className="flex justify-between items-start">
              {/* Left - summary text */}
              <div className="max-w-[520px]">
                <div className="flex items-center gap-3 mb-3">
                  <h3 className="text-[14px] font-bold text-[#1c1c1c]">
                    Reviews summary
                  </h3>
                  <span className="flex items-center gap-1 text-[10px] text-[#888] border border-[#ddd] rounded px-2 py-0.5">
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <circle
                        cx="5"
                        cy="5"
                        r="4"
                        stroke="#888"
                        strokeWidth="0.8"
                      />
                      <path
                        d="M3 5.5l1.5 1.5 3-3"
                        stroke="#888"
                        strokeWidth="0.8"
                      />
                    </svg>
                    Powered by AI
                  </span>
                </div>
                <p className="text-[12px] text-[#444] leading-[1.6] mb-3">
                  {summary.narrative_summary}
                </p>
                {summary.verdict && (
                  <p className="text-[12px] text-[#333] leading-[1.6] mb-4 italic">
                    {summary.verdict}
                  </p>
                )}
                {summary.highlights && summary.highlights.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {summary.highlights.map((h) => (
                      <span
                        key={h}
                        className="bg-[#e8f5e9] text-[#2e7d32] text-[10px] px-2 py-0.5 rounded"
                      >
                        {h}
                      </span>
                    ))}
                    {summary.lowlights &&
                      summary.lowlights.map((l) => (
                        <span
                          key={l}
                          className="bg-[#fce4ec] text-[#c62828] text-[10px] px-2 py-0.5 rounded"
                        >
                          {l}
                        </span>
                      ))}
                  </div>
                )}
                <button className="bg-[#8B6914] text-white text-[12px] px-4 py-1.5 rounded flex items-center gap-1">
                  Jump to all reviews
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path
                      d="M5 2v6M3 6l2 2 2-2"
                      stroke="white"
                      strokeWidth="1"
                    />
                  </svg>
                </button>
              </div>
              {/* Right - ratings */}
              <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                {Object.entries(ratingLabels).map(([key, label]) => (
                  <div key={key} className="flex items-center gap-1.5">
                    <span className="text-[11px] text-[#333] w-[70px]">
                      {label}
                    </span>
                    <RatingDots rating={subRatings[key] || 0} />
                    <span className="text-[11px] text-[#333]">
                      {(subRatings[key] || 0).toFixed(1)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>

        {/* All reviews header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-[18px] font-bold text-[#1c1c1c]">
            All reviews ({summary?.total_reviews_summarized || 1746})
          </h3>
          <button className="border border-[#8B6914] text-[#8B6914] text-[12px] px-4 py-1.5 rounded">
            Write a review
          </button>
        </div>

        {/* Filters bar */}
        <div className="flex items-center gap-3 mb-4">
          <button className="flex items-center gap-1.5 border border-[#ccc] rounded px-3 py-1.5 text-[12px] text-[#333]">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M1 3h10M3 6h6M5 9h2" stroke="#333" strokeWidth="1" />
            </svg>
            Filters (1)
          </button>
          <div className="flex items-center gap-1.5 border border-[#ccc] rounded px-3 py-1.5 text-[12px] text-[#333]">
            Sort by:
            <span className="font-medium">Most recent</span>
            <svg width="8" height="5" viewBox="0 0 8 5" fill="none">
              <path d="M1 1l3 3 3-3" stroke="#333" strokeWidth="1" />
            </svg>
          </div>
          <div className="flex items-center border border-[#ccc] rounded px-3 py-1.5 flex-1 max-w-[200px]">
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              className="mr-1.5"
            >
              <circle cx="5" cy="5" r="4" stroke="#999" strokeWidth="1" />
              <path d="M8 8l3 3" stroke="#999" strokeWidth="1" />
            </svg>
            <input
              type="text"
              placeholder="Search reviews"
              className="text-[12px] outline-none w-full bg-transparent"
            />
          </div>
        </div>

        {/* Popular mentions */}
        <div className="mb-6">
          <span className="text-[12px] text-[#555] mr-2">Popular mentions</span>
          <div className="flex flex-wrap gap-2 mt-2">
            {(summary?.highlights && summary?.lowlights
              ? [...summary.highlights, ...summary.lowlights]
              : [
                  "courtyard fifth ave",
                  "freezing room",
                  "midtown central",
                  "bryant park proximity",
                  "valet parking",
                  "staff helpful",
                  "small rooms",
                  "grand central access",
                  "city view",
                  "noise level",
                ]
            ).map((tag) => (
              <button
                key={tag}
                className="border border-[#ccc] rounded-full px-3 py-1 text-[11px] text-[#333] hover:bg-[#f5f5f5]"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Divider */}
        <hr className="border-[#e0e0e0] mb-6" />

        {/* Review 1 - Jay P */}
        <div className="flex justify-between pb-6 mb-6 border-b border-[#eee]">
          <div className="flex max-w-[550px]">
            <div className="w-[100px] shrink-0">
              <div className="flex items-center gap-1.5 mb-0.5">
                <div className="w-[28px] h-[28px] rounded-full bg-[#e8e8e8] flex items-center justify-center">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="5" r="3" stroke="#999" strokeWidth="1" />
                    <path
                      d="M2 13c0-2.5 2.2-4 5-4s5 1.5 5 4"
                      stroke="#999"
                      strokeWidth="1"
                    />
                  </svg>
                </div>
              </div>
              <span className="text-[12px] font-medium text-[#333]">Jay P</span>
              <div className="text-[10px] text-[#999]">250 contributions</div>
            </div>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <RatingDots rating={1} />
                <span className="text-[12px] text-[#333]">1</span>
                <span className="text-[12px] text-[#999]">•</span>
                <span className="text-[12px] text-[#999]">5 days ago</span>
              </div>
              <h4 className="text-[14px] font-bold text-[#1c1c1c] mb-2">
                Room was Freezing
              </h4>
              <p className="text-[12px] text-[#333] leading-[1.6] mb-4">
                The fact that customers could not control room temperature made
                our stay a little uncomfortable. We had to sleep in layers. When
                we asked if our room temperature was malfunctioning we were told
                they controlled it and could only be changed if they received
                enough complaints.
              </p>
              <div className="flex items-center gap-3 text-[11px] text-[#555]">
                <span>Was it helpful?</span>
                <button className="underline">Yes: 0</button>
                <button className="underline">No: 0</button>
              </div>
            </div>
          </div>
          <div className="shrink-0">
            <div className="flex flex-col gap-2">
              <RatingBar label="Location" value={4.2} color="#8B6914" />
              <RatingBar label="Service" value={3.8} color="#8B6914" />
              <RatingBar
                label="Value for the Money"
                value={2}
                color="#c0392b"
              />
            </div>
          </div>
        </div>

        {/* Review 2 - Sarah L */}
        <div className="flex justify-between pb-6">
          <div className="flex max-w-[550px]">
            <div className="w-[100px] shrink-0">
              <div className="flex items-center gap-1.5 mb-0.5">
                <div className="w-[28px] h-[28px] rounded-full bg-[#e8e8e8] flex items-center justify-center">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="5" r="3" stroke="#999" strokeWidth="1" />
                    <path
                      d="M2 13c0-2.5 2.2-4 5-4s5 1.5 5 4"
                      stroke="#999"
                      strokeWidth="1"
                    />
                  </svg>
                </div>
              </div>
              <span className="text-[12px] font-medium text-[#333]">
                Sarah L.
              </span>
              <div className="text-[10px] text-[#999]">16 contributions</div>
            </div>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <RatingDots rating={4} />
                <span className="text-[12px] text-[#333]">4</span>
                <span className="text-[12px] text-[#999]">•</span>
                <span className="text-[12px] text-[#999]">2 days ago</span>
              </div>
              <h4 className="text-[14px] font-bold text-[#1c1c1c] mb-2">
                Great Location, Compact Room
              </h4>
              <p className="text-[12px] text-[#333] leading-[1.6] mb-4">
                Great central spot noise from street and staff service ans staff
                staff are welicat, and room size with the room size, rooms are
                no arger and great size terrestre.
              </p>
              <div className="flex items-center gap-3 text-[11px] text-[#555]">
                <span>Was it helpful?</span>
                <button className="underline">Yes: 0</button>
                <button className="underline">No: 0</button>
              </div>
            </div>
          </div>
          <div className="shrink-0">
            <div className="flex flex-col gap-2">
              <RatingBar label="Location" value={4.5} color="#8B6914" />
              <RatingBar label="Service" value={4} color="#8B6914" />
              <RatingBar
                label="Value for the Money"
                value={3.5}
                color="#8B6914"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
