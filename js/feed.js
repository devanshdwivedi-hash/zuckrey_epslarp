/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Windows 2000 OS Inset Card & Text Styling
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
      container.innerHTML = `<div class="post-card" style="background-color: #ffffff; border-top: 2px solid #808080; border-left: 2px solid #808080; border-right: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 16px; display: flex; flex-direction: column; position: relative;">
        <p style="color: #800000; font-family: Tahoma, sans-serif; font-size: 1rem; font-weight: bold;"><strong>> ERROR: FAILED TO FETCH FROM ZUCKNET ENGINE</strong></p>
        <p style="color: #333333; font-family: Tahoma, sans-serif; font-size: 0.85rem; margin-top: 6px;">Details: ${fetchError ? fetchError.message : "Backend connection failed."}</p>
      </div>`;
      return;
    }

    const postsList = Array.isArray(rawData) ? rawData : (rawData.posts || []);

    if (!postsList || postsList.length === 0) {
      container.innerHTML = '<p style="color:#000000; padding:15px; font-family:Tahoma, sans-serif; font-size:0.95rem;">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING...</p>';
      return;
    }

    container.innerHTML = "";

    postsList.forEach((post, index) => {
      const postId = post.id || post.post_id || (index + 1);

      let rawDate = post.createdAt || post.created_at || post.timestamp || post.published_at || post.date;

      if (!rawDate) {
        const dateKey = Object.keys(post).find(key => key.toLowerCase().includes('date') || key.toLowerCase().includes('time') || key.toLowerCase().includes('created'));
        if (dateKey) rawDate = post[dateKey];
      }

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

      const card = document.createElement("div");
      card.className = "post-card";
      card.style.cssText = "background-color: #ffffff; border-top: 2px solid #808080; border-left: 2px solid #808080; border-right: 2px solid #ffffff; border-bottom: 2px solid #ffffff; margin: 14px 0; padding: 14px; display: flex; flex-direction: column; position: relative; color: #000000;";
      
      const stampClass = (index % 2 === 0) ? 'stamp-confidential' : 'stamp-redacted';
      const stampText = (index % 2 === 0) ? 'CONFIDENTIAL' : 'REDACTED';

      card.innerHTML = `
        <span class="${stampClass}">${stampText}</span>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #c0c0c0; padding-bottom: 8px; margin-bottom: 12px; padding-right: 110px;">
          <span style="color: #000080; font-weight: bold; font-family: Tahoma, sans-serif; font-size: 1rem; letter-spacing: 0.5px; text-transform: uppercase;">RANT #${postId}</span>
          <span style="color: #333333; font-size: 0.85rem; font-family: Tahoma, monospace;">${formattedDate}</span>
        </div>
        
        <!-- PURE BLACK BODY TEXT FOR PERFECT READABILITY -->
        <div class="post-content" style="color: #000000; font-family: Tahoma, sans-serif; font-size: 0.95rem; line-height: 1.5; display: block; white-space: pre-wrap; margin-bottom: 14px;">${mainText}</div>
        
        <div style="border-top: 1px solid #dfdfdf; padding-top: 8px; font-size: 0.85rem; font-family: Tahoma, sans-serif;">
          <p style="color: #000080; margin: 4px 0; line-height: 1.4;"><strong>> EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p style="color: #333333; margin: 4px 0;"><strong>> SOURCE LINK:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #0000ff; text-decoration: underline; background: #e0e0e0; padding: 2px 4px;">[VIEW SOURCE]</a></p>
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

document.addEventListener("DOMContentLoaded", () => {
  fetchFeed();
  setInterval(fetchFeed, 30000);
  printXFeedLog();
});
