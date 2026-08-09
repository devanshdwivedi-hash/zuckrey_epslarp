/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Dark Burgundy Deep Red Post Cards (#2b1111) & Pinkish-Grey Text (#e6d5d5)
 * Dual Timestamp Metadata Badges: [SOURCE] (Muted) & [AGENT SYNC] (Neon Glow)
 * Points directly to absolute Python Backend URLs (Ports 5000 & 8000)
 */

function formatISTDate(dateInput) {
  if (!dateInput) return null;
  const d = new Date(dateInput);
  if (isNaN(d.getTime())) return null;
  const options = {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  };
  return d.toLocaleString('en-IN', options);
}

function fetchFeed() {
  // Pure root-relative fetch endpoint URL
  const BACKEND_URLS = ["/feed"];

  const container = document.querySelector("#decision-protocols") || 
                    document.querySelector(".feed-container") || 
                    document.querySelector(".scrollable-feed") || 
                    document.getElementById("decision-protocols-container");

  if (!container) {
    console.error("ZUCKNET ERROR: Feed container not found!");
    return;
  }

  async function getFeedData() {
    const fallbackData = [
      {
        title: "Technical Deep Dive: Mitigating Prompt Injection Attacks with a Layered Defense Strategy",
        content: "Technical Deep Dive: Mitigating prompt injection attacks with a layered defense strategy...\n\nSource: Google Security Blog",
        selection_reason: "Selected due to high technical relevance to AI Security & Vulnerability Researcher findings.",
        why_relevant_now: "Critical vulnerability pattern affecting LLM-powered agent workflows in production.",
        sources: ["https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html"],
        source_url: "https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html",
        created_at: new Date().toISOString(),
        timestamp: "08/08/2026, 17:11:38 IST"
      }
    ];

    try {
      let rawData = null;
      let fetchError = null;

      for (const url of BACKEND_URLS) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // 3s timeout
        try {
          const res = await fetch(url, { signal: controller.signal });
          clearTimeout(timeoutId);
          if (res.ok) {
            rawData = await res.json();
            if (rawData && rawData.length > 0) break;
          }
        } catch (err) {
          clearTimeout(timeoutId);
          fetchError = err;
        }
      }

      let postsList = rawData ? (Array.isArray(rawData) ? rawData : (rawData.posts || [])) : [];

      if (!postsList || postsList.length === 0) {
        console.warn("Backend connection failed or timed out. Injecting fallback presentation data.");
        postsList = fallbackData;
      }

      // Sort posts by created_at descending (newest first) & limit feed to 50 posts
      postsList.sort((a, b) => {
        const dateA = new Date(a.created_at || a.createdAt || a.timestamp || a.date || 0).getTime();
        const dateB = new Date(b.created_at || b.createdAt || b.timestamp || b.date || 0).getTime();
        return dateB - dateA;
      });

      postsList = postsList.slice(0, 50);

      container.innerHTML = "";

      postsList.forEach((post, index) => {
        if (!post) return;
        console.log("RAW POST DATA:", post);

        const postId = post.id || post.post_id || (index + 1);

        // 1. AI Agent Sync Timestamp (Neon Glowing style)
        let agentSyncRaw = post.created_at || post.createdAt || post.timestamp || post.date;
        const formattedAgentSync = formatISTDate(agentSyncRaw) || formatISTDate(new Date());
        const agentSyncBadge = `[AGENT SYNC]: ${formattedAgentSync} IST`;
        
        let mainText = (post && (post.text || post.content || post.body || post.rant)) || "No rant text provided by backend.";
        mainText = String(mainText).replace(/[#*`_]/g, "").trim();

        let rationaleText = (post && (post.rationale || post.editorial_rationale || post.selection_reason)) || "No rationale provided.";
        rationaleText = String(rationaleText).replace(/[#*`_]/g, "").trim();

        let sourceUrl = "#";
        if (post && post.sources && Array.isArray(post.sources) && post.sources.length > 0) {
          sourceUrl = post.sources[0];
        } else if (post && post.sources && typeof post.sources === "string") {
          sourceUrl = post.sources;
        } else if (post && (post.source || post.source_url)) {
          sourceUrl = post.source || post.source_url;
        }

        const card = document.createElement("div");
        card.className = "post-card";
        card.style.cssText = "background-color: #2b1111; border: 1px solid #522525; margin: 14px 0; padding: 14px; display: flex; flex-direction: column; position: relative; color: #e6d5d5; box-shadow: 0 4px 12px rgba(0,0,0,0.6);";
        
        const stampClass = (index % 2 === 0) ? 'stamp-confidential' : 'stamp-redacted';
        const stampText = (index % 2 === 0) ? 'CONFIDENTIAL' : 'REDACTED';

        card.innerHTML = `
          <span class="${stampClass}">${stampText}</span>
          <div style="display: flex; flex-direction: column; gap: 4px; border-bottom: 1px solid #522525; padding-bottom: 8px; margin-bottom: 12px; padding-right: 120px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
              <span style="color: #ff6666; font-weight: bold; font-family: Tahoma, sans-serif; font-size: 1rem; letter-spacing: 0.5px; text-transform: uppercase;">RANT #${postId}</span>
              <span class="badge-agent-sync" style="color: #33ff00; font-size: 0.85rem; font-family: Tahoma, monospace; font-weight: bold; text-shadow: 0 0 6px rgba(51, 255, 0, 0.6);">${agentSyncBadge}</span>
            </div>
          </div>
          
          <!-- PINKISH-GREY RETRO SCROLLABLE TEXT BOX (#e6d5d5) -->
          <div class="post-content rant-text-body" style="color: #e6d5d5; font-family: Tahoma, sans-serif; font-size: 0.95rem; line-height: 1.5; text-shadow: 0 0 2px rgba(0,0,0,1); max-height: 150px; overflow-y: auto; padding-right: 10px; margin-bottom: 10px; border: 1px solid #455945; background-color: rgba(0, 0, 0, 0.2); white-space: pre-wrap;">${mainText}</div>
          
          <div style="border-top: 1px solid #522525; padding-top: 8px; font-size: 0.85rem; font-family: Tahoma, sans-serif;">
            <p style="color: #8ca68c; margin: 4px 0; line-height: 1.4;"><strong>> EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
            <p style="color: #b3b3b3; margin: 4px 0;"><strong>> SOURCE LINK:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #33ff00; text-decoration: underline; background: #1a0a0a; padding: 2px 4px;">[VIEW SOURCE]</a></p>
          </div>
        `;
        
        container.appendChild(card);
      });
    } catch (err) {
      console.error("FEED CRASH:", err);
      container.innerHTML = `<div style="color: red; padding: 20px; font-family: monospace;">CRITICAL FEED ERROR: ${err.message}</div>`;
    }
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

document.addEventListener("DOMContentLoaded", () => {
  fetchFeed();
  setInterval(fetchFeed, 30000);
  printXFeedLog();
});
