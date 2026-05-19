import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Brain,
  ShieldPlus,
  FileText,
  Send,
  Sparkles,
  Zap,
  Eye,
  Shield,
  Scan,
} from "lucide-react";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

/* ============================================================
   SCANNING OVERLAY — Cinematic "AI Processing" Effect
   ============================================================ */
function ScanOverlay({ label }: { label: string }) {
  const stages = [
    "Initializing neural pathways",
    "Cross-referencing symptom database",
    "Running differential analysis",
    "Consulting knowledge graph",
    "Synthesizing clinical output",
  ];

  const [activeStage, setActiveStage] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 800);

    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 2, 95));
    }, 100);

    return () => {
      clearInterval(interval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="scan-overlay"
    >
      {/* Spinning Rings */}
      <div className="scan-ring">
        <motion.div
          style={{
            position: "absolute",
            inset: "35%",
            borderRadius: "50%",
            background: "radial-gradient(circle, var(--neon) 0%, transparent 70%)",
          }}
          animate={{
            scale: [0.8, 1.2, 0.8],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </div>

      {/* Main Label */}
      <motion.div
        className="scan-text"
        animate={{ opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        {label}
      </motion.div>

      {/* Progress Bar */}
      <div className="progress-track">
        <motion.div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Fake Processing Stages */}
      <div className="scan-nodes">
        {stages.map((stage, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.15 }}
            className={`scan-node ${
              i < activeStage ? "done" : i === activeStage ? "active" : ""
            }`}
          >
            <div className="scan-node-dot" />
            <span>{stage}</span>
            {i < activeStage && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.5 }}
                style={{ marginLeft: "auto", fontSize: "0.65rem" }}
              >
                ✓
              </motion.span>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

/* ============================================================
   TIMELINE — Glowing Progress Nodes
   ============================================================ */
function Timeline({ step }: { step: string }) {
  const steps = [
    { key: "start", label: "Symptoms", icon: Brain },
    { key: "questioning", label: "AI Interview", icon: Activity },
    { key: "physician", label: "Physician", icon: ShieldPlus },
    { key: "report", label: "Report", icon: FileText },
  ];

  const currentIdx = steps.findIndex((s) => s.key === step);

  return (
    <div className="timeline-container">
      {steps.map((s, i) => {
        const isActive = s.key === step;
        const isCompleted = i < currentIdx;

        return (
          <div key={s.key} style={{ display: "flex", alignItems: "center" }}>
            <div className="timeline-node">
              <motion.div
                className={`timeline-circle ${
                  isActive
                    ? "active-node"
                    : isCompleted
                    ? "completed-node"
                    : ""
                }`}
                layout
              />
              <span
                className={`timeline-label ${
                  isActive
                    ? "active-label"
                    : isCompleted
                    ? "completed-label"
                    : ""
                }`}
              >
                {s.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={`timeline-connector ${
                  isCompleted
                    ? "completed-connector"
                    : isActive
                    ? "active-connector"
                    : ""
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ============================================================
   GLASS CARD — Animated Container
   ============================================================ */
function GlassCard({ children, id }: { children: React.ReactNode; id?: string }) {
  return (
    <motion.div
      id={id}
      initial={{ opacity: 0, y: 40, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -30, scale: 0.97 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="glass-card"
    >
      {children}
    </motion.div>
  );
}

/* ============================================================
   MAIN APP
   ============================================================ */
export default function App() {
  const [step, setStep] = useState<
    "start" | "questioning" | "physician" | "report"
  >("start");

  const [complaint, setComplaint] = useState("");
  const [threadId, setThreadId] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [questionCount, setQuestionCount] = useState(0);
  const [history, setHistory] = useState<
    { question: string; answer: string }[]
  >([]);

  const [summary, setSummary] = useState("");
  const [interimCare, setInterimCare] = useState("");

  const [treatment, setTreatment] = useState("");
  const [comments, setComments] = useState("");
  const [approved, setApproved] = useState(true);

  const [finalReport, setFinalReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [scanLabel, setScanLabel] = useState("Processing");

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, currentQuestion]);

  /* ---- API Calls ---- */

  const startConsultation = async () => {
    if (!complaint.trim()) return;
    try {
      setLoading(true);
      setScanLabel("Initializing Diagnostic Ritual");

      const res = await API.post("/consultation/start", {
        initial_complaint: complaint,
      });

      setThreadId(res.data.thread_id);
      setCurrentQuestion(res.data.current_question);
      setQuestionCount(res.data.question_count);
      setStep("questioning");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const sendAnswer = async () => {
    if (!answer.trim()) return;
    try {
      setLoading(true);
      setScanLabel("Analyzing Response");

      const res = await API.post("/consultation/resume", {
        thread_id: threadId,
        answer,
      });

      setHistory((prev) => [
        ...prev,
        { question: currentQuestion, answer },
      ]);

      setQuestionCount(res.data.question_count);
      const status = res.data.status;

      if (status === "awaiting_physician" || status === "awaiting_md") {
        setSummary(res.data.diagnostic_summary || "");
        setInterimCare(res.data.interim_care || "");
        setStep("physician");
      } else {
        setCurrentQuestion(res.data.current_question);
      }

      setAnswer("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const submitReview = async () => {
    try {
      setLoading(true);
      setScanLabel("Generating Final Report");

      const res = await API.post("/physician/review", {
        thread_id: threadId,
        treatment,
        approved,
        comments,
      });

      setFinalReport(res.data.final_report || "");
      setStep("report");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setStep("start");
    setComplaint("");
    setThreadId("");
    setCurrentQuestion("");
    setAnswer("");
    setQuestionCount(0);
    setHistory([]);
    setSummary("");
    setInterimCare("");
    setTreatment("");
    setComments("");
    setApproved(true);
    setFinalReport("");
  };

  const handleKeyDown = (
    e: React.KeyboardEvent,
    action: () => void
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      action();
    }
  };

  return (
    <div className="bg-main" style={{ minHeight: "100vh", position: "relative", overflow: "hidden" }}>
      {/* Particle Layer */}
      <div className="particles" style={{ position: "absolute", inset: 0 }} />

      <div className="container-main">
        {/* ---- Header ---- */}
        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="text-center mb-10"
        >
          <motion.img
            src="/images/asclepios-logo.gif"
            alt="ASCLEPIOS O.T Logo"
            style={{
              width: "300px",
              margin: "0 auto 24px",
              display: "block",
            }}
            className="neon-logo"
            animate={{
              scale: [1, 1.03, 1],
              opacity: [0.85, 1, 0.85],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          <h1
            className="neon-text"
            style={{
              fontSize: "clamp(2rem, 5vw, 3.5rem)",
              fontWeight: 700,
              letterSpacing: "0.15em",
              marginBottom: "12px",
            }}
          >
            ASCLEPIOS O.T
          </h1>

          <motion.p
            style={{
              color: "var(--text-secondary)",
              fontSize: "1rem",
              letterSpacing: "0.1em",
              fontWeight: 300,
            }}
            animate={{ opacity: [0.6, 0.9, 0.6] }}
            transition={{ duration: 5, repeat: Infinity }}
          >
            ⟁ Mystical AI Clinical Orientation System ⟁
          </motion.p>
        </motion.div>

        {/* ---- Timeline ---- */}
        <Timeline step={step} />

        {/* ---- Step Content ---- */}
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {/* ======== START ======== */}
            {step === "start" && (
              <GlassCard key="start" id="step-start">
                <div className="section-heading mb-8">
                  <Brain size={28} className="icon" />
                  <h2>Begin Consultation</h2>
                </div>

                <div className="mb-3" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <Sparkles size={14} style={{ color: "var(--neon-dim)", opacity: 0.6 }} />
                  <span style={{ color: "var(--text-muted)", fontSize: "0.8rem", letterSpacing: "1px", textTransform: "uppercase" }}>
                    Describe the patient's symptoms
                  </span>
                </div>

                <textarea
                  id="complaint-input"
                  value={complaint}
                  onChange={(e) => setComplaint(e.target.value)}
                  onKeyDown={(e) => handleKeyDown(e, startConsultation)}
                  placeholder="e.g. Patient presents with persistent chest pain, shortness of breath, radiating to left arm..."
                  className="mystical-input"
                  style={{ height: "200px" }}
                />

                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "24px", marginTop: "24px" }}>
                  <motion.button
                    id="btn-start"
                    onClick={startConsultation}
                    className="neon-button"
                    disabled={!complaint.trim()}
                    whileTap={{ scale: 0.97 }}
                  >
                    <Zap size={18} />
                    Initialize Diagnostic Ritual
                  </motion.button>
                  <img
                    src="/images/writedown_transparent_latest.gif"
                    alt="Write Down"
                    className="floating-gif"
                    style={{ height: "120px" }}
                  />
                </div>
              </GlassCard>
            )}

            {/* ======== QUESTIONING ======== */}
            {step === "questioning" && (
              <GlassCard key="questioning" id="step-questioning">
                <div
                  className="mb-8"
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "16px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                    <div className="section-heading">
                      <Activity size={28} className="icon" />
                      <h2>AI Interview Sequence</h2>
                    </div>
                    <img
                      src="/images/video_1.gif"
                      alt="AI Sequence"
                      className="floating-gif"
                      style={{ height: "40px", borderRadius: "4px" }}
                    />
                  </div>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      color: "var(--neon-dim)",
                      fontSize: "0.85rem",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    <Eye size={14} />
                    <span>
                      Q{questionCount + 1}
                      <span style={{ opacity: 0.4 }}>/5</span>
                    </span>
                  </div>
                </div>

                {/* Chat History */}
                <div
                  style={{
                    maxHeight: "400px",
                    overflowY: "auto",
                    paddingRight: "8px",
                    marginBottom: "24px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "16px",
                  }}
                >
                  {history.map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      style={{ display: "flex", flexDirection: "column", gap: "12px" }}
                    >
                      <div className="ai-bubble">{item.question}</div>
                      <div className="user-bubble">{item.answer}</div>
                    </motion.div>
                  ))}

                  {/* Current Question */}
                  <motion.div
                    key={`q-${questionCount}`}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="ai-bubble"
                  >
                    {currentQuestion}
                  </motion.div>

                  <div ref={chatEndRef} />
                </div>

                {/* Input */}
                <div style={{ display: "flex", gap: "12px" }}>
                  <input
                    id="answer-input"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, sendAnswer)}
                    placeholder="Your answer..."
                    className="mystical-input flex-1"
                    style={{ height: "56px", resize: "none" }}
                  />

                  <motion.button
                    id="btn-send"
                    onClick={sendAnswer}
                    className="send-button"
                    disabled={!answer.trim()}
                    whileTap={{ scale: 0.92 }}
                    whileHover={{ scale: 1.05 }}
                  >
                    <Send size={20} />
                  </motion.button>
                </div>
              </GlassCard>
            )}

            {/* ======== PHYSICIAN REVIEW ======== */}
            {step === "physician" && (
              <GlassCard key="physician" id="step-physician">
                <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "32px" }}>
                  <div className="section-heading" style={{ marginBottom: 0 }}>
                    <ShieldPlus size={28} className="icon" />
                    <h2>Physician Review Chamber</h2>
                  </div>
                  <img
                    src="/images/video_2.gif"
                    alt="Physician Review"
                    className="floating-gif"
                    style={{ height: "40px", borderRadius: "4px" }}
                  />
                </div>

                {/* Summary & Interim Care */}
                <div className="grid-2 mb-8">
                  <motion.div
                    className="sub-card"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <div className="sub-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <Scan size={14} />
                      Clinical Summary
                    </div>
                    <p
                      className="whitespace-pre-wrap"
                      style={{ color: "var(--text-primary)", lineHeight: 1.7, fontSize: "0.9rem" }}
                    >
                      {summary || "Awaiting diagnostic data..."}
                    </p>
                  </motion.div>

                  <motion.div
                    className="sub-card"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <div className="sub-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <Shield size={14} />
                      Interim Care
                    </div>
                    <p
                      className="whitespace-pre-wrap"
                      style={{ color: "var(--text-primary)", lineHeight: 1.7, fontSize: "0.9rem" }}
                    >
                      {interimCare || "No interim care data available."}
                    </p>
                  </motion.div>
                </div>

                {/* Physician Inputs */}
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="mb-2" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem", letterSpacing: "1.5px", textTransform: "uppercase" }}>
                      Treatment / Recommendation
                    </span>
                  </div>
                  <textarea
                    id="treatment-input"
                    value={treatment}
                    onChange={(e) => setTreatment(e.target.value)}
                    placeholder="Prescribe treatment or add clinical recommendations..."
                    className="mystical-input mb-6"
                    style={{ height: "140px" }}
                  />

                  <div className="mb-2" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem", letterSpacing: "1.5px", textTransform: "uppercase" }}>
                      Additional Comments
                    </span>
                  </div>
                  <textarea
                    id="comments-input"
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    placeholder="Any additional notes or observations..."
                    className="mystical-input mb-6"
                    style={{ height: "110px" }}
                  />

                  <label className="mystical-checkbox mb-8">
                    <input
                      type="checkbox"
                      checked={approved}
                      onChange={(e) => setApproved(e.target.checked)}
                    />
                    Approve clinical synthesis
                  </label>

                  <motion.button
                    id="btn-validate"
                    onClick={submitReview}
                    className="neon-button"
                    whileTap={{ scale: 0.97 }}
                  >
                    <ShieldPlus size={18} />
                    Validate Consultation
                  </motion.button>
                </motion.div>
              </GlassCard>
            )}

            {/* ======== FINAL REPORT ======== */}
            {step === "report" && (
              <GlassCard key="report" id="step-report">
                <div className="section-heading mb-8">
                  <FileText size={28} className="icon" />
                  <h2>Final Clinical Report</h2>
                </div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="report-card whitespace-pre-wrap mb-8"
                >
                  {finalReport || "Report generation in progress..."}
                </motion.div>

                <motion.button
                  id="btn-reset"
                  onClick={resetApp}
                  className="neon-button"
                  whileTap={{ scale: 0.97 }}
                >
                  <Sparkles size={18} />
                  Start New Consultation
                </motion.button>
              </GlassCard>
            )}
          </AnimatePresence>
        </div>

        {/* ---- Footer ---- */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          style={{
            textAlign: "center",
            marginTop: "64px",
            paddingBottom: "32px",
            color: "var(--text-muted)",
            fontSize: "0.7rem",
            letterSpacing: "2px",
            textTransform: "uppercase",
          }}
        >
          ASCLEPIOS O.T — Multi-Agent Clinical System — Powered by LangGraph
        </motion.div>
      </div>

      {/* ---- Loading Overlay ---- */}
      <AnimatePresence>
        {loading && <ScanOverlay label={scanLabel} />}
      </AnimatePresence>
    </div>
  );
}
