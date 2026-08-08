/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Deep Red Dark-Web Decision Protocol Cards & Asymmetrical Rotations
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
      container.innerHTML = `<div class="post-card" style="background-color: #2b1111; border: 1px solid #732222; padding: 16px; display: flex; flex-direction: column; position: relative;">
        <p style="color: #c45656; font-family: 'Arial Narrow', sans-serif; font-size: 1rem; font-weight: bold;"><strong>> ERROR: FAILED TO FETCH FROM ZUCKNET ENGINE</strong></p>
        <p style="color: #997373; font-family: 'Courier New', monospace; font-size: 0.85rem; margin-top: 6px;">Details: ${fetchError ? fetchError.message : "Backend connection failed."}</p>
      </div>`;
      return;
    }

    const postsList = Array.isArray(rawData) ? rawData : (rawData.posts || []);

    if (!postsList || postsList.length === 0) {
      container.innerHTML = '<p style="color:#a88a8a; padding:15px; font-family:\'Courier New\', monospace; font-size:0.95rem;">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING...</p>';
      return;
    }

    // Wipe out placeholders before injecting new data
    container.innerHTML = "";

    postsList.forEach((post, index) => {
      // 1. Safe Key Extraction
      const postId = post.id || post.post_id || (index + 1);

      // Aggressive Timestamp Extraction
      let rawDate = post.createdAt || post.created_at || post.timestamp || post.published_at || post.date;

      if (!rawDate) {
        const dateKey = Object.keys(post).find(key => key.toLowerCase().includes('date') || key.toLowerCase().includes('time') || key.toLowerCase().includes('created'));
        if (dateKey) rawDate = post[dateKey];
      }

      // Format into strict Y2K terminal timestamp: [YYYY-MM-DD // HH:MM:SS UTC]
      let formattedDate = "[TIMESTAMP NULL]";
      if (rawDate) {
        const d = new Date(rawDate);
        if (!isNaN(d.getTime())) {
          const yyyy = d.getUTCFullYear();
          const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
          const dd = String(d.getUTCDate()).padStart(2, '0');
          const hh = String(d.getUTCHours()).padStart(2, '0');
          const min = String(d.getUTCMinutes()).padStart(2, '0');
          const sec = String(d.getUTCSeconds()).padStart(2, '0');
          formattedDate = `[${yyyy}-${mm}-${dd} // ${hh}:${min}:${sec} UTC]`;
        }
      }
      
      // 2. Markdown Sanitization
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

      // 3. Deep Red "Decision Protocol" Card DOM Element with Asymmetrical Rotation
      const card = document.createElement("div");
      card.className = "post-card";
      card.style.cssText = "background-color: #2b1111; border: 1px solid #522525; margin: 20px 0; padding: 14px; display: flex; flex-direction: column; position: relative; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.6);";
      
      // Add slight random rotation to each card as it generates for a chaotic feel
      card.style.transform = Math.random() > 0.5 ? 'rotate(-0.5deg)' : 'rotate(0.5deg)';

      const stampClass = (index % 2 === 0) ? 'stamp-confidential' : 'stamp-redacted';
      const stampText = (index % 2 === 0) ? 'CONFIDENTIAL' : 'REDACTED';

      card.innerHTML = `
        <span class="${stampClass}">${stampText}</span>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #522525; padding-bottom: 8px; margin-bottom: 12px; padding-right: 110px;">
          <span style="color: #d9b8b8; font-weight: bold; font-family: 'Arial Narrow', 'Impact', sans-serif; font-size: 1.05rem; letter-spacing: 1px; text-transform: uppercase;">RANT #${postId}</span>
          <span style="color: #cfa856; font-size: 0.85rem; font-family: 'Courier New', monospace;">${formattedDate}</span>
        </div>
        
        <!-- LEGIBLE GREY-RED BODY TEXT (#a88a8a) -->
        <div class="post-content" style="color: #a88a8a; font-family: 'Courier New', monospace; font-size: 0.95rem; line-height: 1.5; display: block; white-space: pre-wrap; margin-bottom: 14px;">${mainText}</div>
        
        <div style="border-top: 1px solid #421e1e; padding-top: 8px; font-size: 0.85rem; font-family: 'Courier New', monospace;">
          <p style="color: #d4a359; margin: 4px 0; line-height: 1.4;"><strong>> EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p style="color: #b88a8a; margin: 4px 0;"><strong>> SOURCE LINK:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #b88a8a; text-decoration: underline; background: #1c0a0a; padding: 2px 4px;">[VIEW SOURCE]</a></p>
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

// Initialize and set 30-second interval
document.addEventListener("DOMContentLoaded", () => {
  fetchFeed();
  setInterval(fetchFeed, 30000);
  printXFeedLog();
});
