import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Start the Python backend server
let pythonServer = null;
const startPythonServer = () => {
  console.log("Starting Python backend server...");
  pythonServer = spawn("python", ["-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"], {
    cwd: path.join(__dirname, "..", "backend"),
    stdio: "pipe"
  });

  pythonServer.stdout.on("data", (data) => {
    console.log(`Python backend: ${data}`);
  });

  pythonServer.stderr.on("data", (data) => {
    console.error(`Python backend error: ${data}`);
  });

  pythonServer.on("close", (code) => {
    console.log(`Python backend exited with code ${code}`);
  });
};

// Start Python server
startPythonServer();

// Proxy API requests to Python backend
app.use("/api", async (req, res) => {
  try {
    const url = `http://localhost:8001${req.originalUrl}`;
    const response = await fetch(url, {
      method: req.method,
      headers: {
        "Content-Type": "application/json",
        ...req.headers
      },
      body: req.method !== "GET" ? JSON.stringify(req.body) : undefined
    });

    const data = await response.text();
    res.status(response.status);
    
    // Set content type based on response
    const contentType = response.headers.get("content-type");
    if (contentType) {
      res.set("Content-Type", contentType);
    }
    
    res.send(data);
  } catch (error) {
    console.error("Proxy error:", error);
    res.status(500).json({ error: "Backend service unavailable" });
  }
});

// Health check endpoint
app.get("/health", (_, res) => res.json({ ok: true, service: "express-proxy" }));

// Serve the SPA
const dist = path.join(__dirname, "..", "dist");
app.use(express.static(dist));
app.get("*", (_, res) => {
  res.sendFile(path.join(dist, "index.html"));
});

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("Received SIGTERM, shutting down gracefully");
  if (pythonServer) {
    pythonServer.kill();
  }
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("Received SIGINT, shutting down gracefully");
  if (pythonServer) {
    pythonServer.kill();
  }
  process.exit(0);
});

app.listen(PORT, () => {
  console.log(`API + UI listening on :${PORT}`);
});
