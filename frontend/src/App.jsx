import { useState } from "react";
import axios from "axios";

function App() {
  const [link, setLink] = useState("");
  const [desc, setDesc] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Backend API URL
  const API_URL = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const { data } = await axios.post(`${API_URL}/check`, {
        link,
        description: desc,
        email,
      });
      setResult(data);
    } catch (err) {
      if (err.response) {
        setResult({ error: err.response.data || err.response.statusText });
      } else if (err.request) {
        setResult({
          error: "No response from backend. Check if server is running.",
        });
      } else {
        setResult({ error: err.message });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: "40px auto", padding: 16 }}>
      <h1>Internship Credibility Checker</h1>
      <p>Paste an internship link or description to get a first-pass check.</p>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <label>
          Internship Link (optional)
          <input
            type="url"
            placeholder="https://example.com/posting"
            value={link}
            onChange={(e) => setLink(e.target.value)}
            style={{ width: "100%", padding: 8 }}
          />
        </label>

        <label>
          Contact Email (optional)
          <input
            type="email"
            placeholder="hr@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ width: "100%", padding: 8 }}
          />
        </label>

        <label>
          Description (paste the text)
          <textarea
            rows={6}
            placeholder="Paste the internship description here..."
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            style={{ width: "100%", padding: 8 }}
            required
          />
        </label>

        <button type="submit" disabled={loading} style={{ padding: 10 }}>
          {loading ? "Checking..." : "Check Credibility"}
        </button>
      </form>

      {/* ✅ Updated Result Block */}
      <div style={{ marginTop: 24 }}>
        <h2>Result</h2>
        {!result && <p>No result yet.</p>}

        {result?.error && <p style={{ color: "red" }}>{result.error}</p>}

        {result && !result.error && (
          <div style={{ border: "1px solid #eee", borderRadius: 8, padding: 16 }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <span
                style={{
                  padding: "4px 10px",
                  borderRadius: 999,
                  color: "white",
                  background:
                    result.status === "Real"
                      ? "#16a34a"
                      : result.status === "Fake"
                      ? "#dc2626"
                      : "#f59e0b",
                }}
              >
                {result.status}
              </span>
              <strong>Credibility:</strong> {result.credibility}/100
            </div>

            {/* progress bar */}
            <div style={{ marginTop: 10, height: 10, background: "#eee", borderRadius: 6 }}>
              <div
                style={{
                  height: "100%",
                  width: `${result.credibility}%`,
                  borderRadius: 6,
                  background:
                    result.credibility >= 75
                      ? "#16a34a"
                      : result.credibility <= 40
                      ? "#dc2626"
                      : "#f59e0b",
                }}
              />
            </div>

            {/* paid/unpaid */}
            {result.paid !== null && (
              <p style={{ marginTop: 10 }}>
                <strong>Paid:</strong> {result.paid ? "Yes" : "No"}
              </p>
            )}

            {/* explanations */}
            <div style={{ marginTop: 10 }}>
              <strong>Why:</strong>
              <ul>
                {result.explanations?.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      <footer style={{ marginTop: 40, opacity: 0.7 }}>
        <small>Dev API base: {API_URL}</small>
      </footer>
    </div>
  );
}

export default App;
