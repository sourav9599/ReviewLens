import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { Loader2, RefreshCw } from "lucide-react";
import { useReviewStore } from "../store/reviewStore";
import DashboardPage from "./DashboardPage";

const API_BASE = "http://localhost:5000/api";

export default function PropertyDashboardPage() {
  const { propertyCode } = useParams();
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);

  const setReport = useReviewStore((s) => s.setReport);
  const setJobStatus = useReviewStore((s) => s.setJobStatus);

  const triggerAnalysis = async (forceRefresh = false) => {
    setStatus("loading");
    setError(null);

    try {
      const { data } = await axios.post(
        `${API_BASE}/analyze/property/${propertyCode}?force_refresh=${forceRefresh}`
      );

      if (data.from_cache && data.report) {
        setReport(data.report);
        setJobStatus("complete");
        setStatus("ready");
      } else if (data.job_id) {
        setJobId(data.job_id);
        setStatus("processing");
        pollJob(data.job_id);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`No reviews found for property "${propertyCode}". Run ingestion first.`);
      } else {
        setError(err.message || "Failed to trigger analysis");
      }
      setStatus("error");
    }
  };

  const pollJob = (id) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get(`${API_BASE}/jobs/${id}`);

        if (data.status === "complete" && data.report) {
          clearInterval(interval);
          setReport(data.report);
          setJobStatus("complete");
          setStatus("ready");
        } else if (data.status === "failed") {
          clearInterval(interval);
          setError(data.error || "Analysis pipeline failed");
          setStatus("error");
        }
      } catch {
        clearInterval(interval);
        setError("Lost connection to server");
        setStatus("error");
      }
    }, 3000);
  };

  useEffect(() => {
    if (propertyCode) {
      triggerAnalysis(false);
    }
  }, [propertyCode]);

  if (status === "loading" || status === "processing") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 size={36} className="animate-spin text-orange-500" />
        <p className="text-sm text-gray-600 font-medium">
          {status === "loading"
            ? `Loading analysis for ${propertyCode}...`
            : `Running analysis pipeline for ${propertyCode}...`}
        </p>
        <p className="text-xs text-gray-400">This may take a minute on first run (results are cached)</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="text-center">
          <p className="text-sm text-red-600 font-medium mb-2">{error}</p>
          <button
            onClick={() => triggerAnalysis(true)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-orange-500 rounded-lg hover:bg-orange-600 transition"
          >
            <RefreshCw size={14} /> Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  return <DashboardPage />;
}
