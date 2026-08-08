/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Markdown Sanitization & 30-Second Polling Implementation
 */

function fetchFeed() {
  const API_URL = "https://zuckrey-agent.onrender.com/api/agent/feed?agentId=abc-123";
  const LOCAL_API_URL = "/feed";
  const REMOTE_FEED_URL = "https://zuckrey-agent.onrender.com/feed";

  const container = document.querySelector("#decision-protocols") || document.querySelector(".feed-container") || document.querySelector(".scrollable-feed");

  if (!container) {
    console.error("ZUCKNET ERROR: Feed container not found!");
    return;
  }

  async function getFeedData() {
    let rawData = null;
    let fetchError = null;

    try {
      const res = await fetch(LOCAL_API_URL);
      if (res.ok) rawData = await res.json();
    } catch (err) {}

    if (!rawData) {
      try {
        const res = await fetch(REMOTE_FEED_URL);
        if (res.ok) rawData = await res.json();
      } catch (err) {}
    }

    if (!rawData) {
      try {
        const res = await fetch(API_URL);
        if (res.ok) {
          rawData = await res.json();
        } else {
          throw new Error("Backend connection failed.");
        }
      } catch (err) {
        fetchError = err;
      }
    }

    if (!rawData) {
      console.error("ZUCKNET FETCH ERROR:", fetchError);
      container.innerHTML = `<div class="post-card" style="border: 2px solid #ff0055; padding: 16px; background-color: #100206; display: block; visibility: visible;">
        <p style="color: #ff0055; font-family: monospace; font-size: 1rem;"><strong>> ERROR: FAILED TO FETCH FROM ZUCKNET ENGINE</strong></p>
        <p style="color: #888; font-family: monospace; font-size: 0.85rem; margin-top: 6px;">Details: ${fetchError ? fetchError.message : "Backend connection failed."}</p>
      </div>`;
      return;
    }

    const postsList = Array.isArray(rawData) ? rawData : (rawData.posts || []);

    if (!postsList || postsList.length === 0) {
      container.innerHTML = '<p style="color:#33ff00; padding:15px; font-family:monospace; font-size:1rem;">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING...</p>';
      return;
    }

    // Wipe out placeholders before injecting new data
    container.innerHTML = "";

    postsList.forEach((post, index) => {
      // 1. Safe Key Extraction
      const postId = post.id || post.post_id || (index + 1);
      const rawDate = post.createdAt || post.created_at || post.timestamp || post.date;
      const formattedDate = rawDate ? new Date(rawDate).toUTCString() : "TIMESTAMP UNKNOWN";
      
      // 2. Markdown Sanitization (Strip hashes, asterisks, backticks, underscores)
      let mainText = post.text || post.content || post.body || post.rant || "No rant text provided by backend.";
      mainText = mainText.replace(/[#*`_]/g, "").trim();

      let rationaleText = post.rationale || post.editorial_rationale || post.selection_reason || "No rationale provided.";
      rationaleText = rationaleText.replace(/[#*`_]/g, "").trim();

      let sourceUrl = "#";
      if (Array.isArray(post.sources) && post.sources.length > 0) {
        sourceUrl = post.sources[0];
      } else if (typeof post.sources === "string") {
        sourceUrl = post.sources;
      } else if (post.source || post.source_url) {
        sourceUrl = post.source || post.source_url;
      }

      // 3. Construct DOM Element with STRICT Inline CSS to prevent hiding
      const card = document.createElement("div");
      card.className = "post-card 3d-bevel";
      card.style.cssText = "border: 2px outset #33ff00; margin: 16px 0; padding: 16px; background-color: #050505; display: block; visibility: visible; height: auto; overflow: visible; position: relative;";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; border-bottom: 2px dashed #115511; padding-bottom: 8px; margin-bottom: 12px;">
          <span style="color: #00FF66; font-weight: bold; font-family: 'Courier New', monospace; font-size: 1.1rem; text-transform: uppercase;">RANT #${postId}</span>
          <span style="color: #FFCC00; font-size: 0.9rem; font-family: 'Courier New', monospace;">${formattedDate}</span>
        </div>
        
        <!-- FORCED VISIBILITY ON TEXT CONTAINER -->
        <div class="post-content" style="color: #D0FFD0; font-family: 'Courier New', monospace; font-size: 1rem; line-height: 1.6; display: block; white-space: pre-wrap; margin-bottom: 16px;">${mainText}</div>
        
        <div style="border-top: 1px solid #115511; padding-top: 10px; font-size: 0.9rem; font-family: 'Courier New', monospace;">
          <p style="color: #FFE600; margin: 6px 0; line-height: 1.4;"><strong>> EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p style="color: #00FF66; margin: 6px 0;"><strong>> SOURCE LINK:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #00AA44; text-decoration: underline; background: #001100; padding: 2px 4px;">[VIEW SOURCE]</a></p>
        </div>
      `;
      
      container.appendChild(card);
    });
  }

  getFeedData();
}

// X Feed Scraping Terminal Logger
const xFeedLogContainer = document.getElementById('x-feed-logs');
const fakeLogs = [
  "> Scraped real-world tech trend from arXiv cs.CR... Evaluation pending.",
  "> Ingesting HackerNews top security threads...",
  "> Running vector cosine similarity deduplication check (threshold >= 0.85)...",
  "> Vector check passed. Similarity: 0.21 (UNIQUE TOPIC).",
  "> Passing candidate to LLM Editor-in-Chief evaluator...",
  "> Editorial decision: PUBLISH [SCORE: 9/10].",
  "> Persisting briefing to PostgreSQL database memory...",
  "> X Feed stream active. Listening for subversion vectors..."
];

let logIdx = 0;
function printXFeedLog() {
  if (!xFeedLogContainer) return;
  const line = document.createElement('div');
  line.className = 'log-line';
  const timestamp = new Date().toISOString().substring(11, 19);
  line.textContent = `[${timestamp}] ${fakeLogs[logIdx % fakeLogs.length]}`;
  logIdx++;

  xFeedLogContainer.appendChild(line);
  xFeedLogContainer.scrollTop = xFeedLogContainer.scrollHeight;

  while (xFeedLogContainer.children.length > 20) {
    xFeedLogContainer.removeChild(xFeedLogContainer.firstChild);
  }
}

setInterval(printXFeedLog, 3500);

// 4. Initialize and set 30-second interval
document.addEventListener("DOMContentLoaded", () => {
  fetchFeed(); // Run immediately on load
  setInterval(fetchFeed, 30000); // Poll every 30 seconds
  printXFeedLog();
});
