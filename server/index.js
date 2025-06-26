import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { createProxyMiddleware } from "http-proxy-middleware";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

// Proxy API requests to FastAPI backend running on port 8000
app.use("/api", createProxyMiddleware({
  target: "http://localhost:8000",
  changeOrigin: true,
  onError: (err, req, res) => {
    console.error("Proxy error:", err);
    res.status(500).json({ error: "Backend service unavailable" });
  },
}));

// Health check endpoint
app.get("/health", (_, res) => res.json({ok: true}));

// Serve SPA
const dist = path.join(__dirname, "..", "dist");
app.use(express.static(dist));
app.get("*", (_, res) => res.sendFile(path.join(dist, "index.html")));

app.listen(PORT, () => console.log(`Frontend server running on port ${PORT}`));
