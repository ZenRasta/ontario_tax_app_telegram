import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

// Existing /api routes
app.get("/api/health", (_, res) => res.json({ok: true}));

// Serve SPA
const dist = path.join(__dirname, "..", "dist");
app.use(express.static(dist));
app.get("*", (_, res) => res.sendFile(path.join(dist, "index.html")));

app.listen(PORT, () => console.log(`API + UI on :${PORT}`));
