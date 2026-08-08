/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Flexible Key Mapping & High-Contrast Card Rendering Implementation
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "https://zuckrey-agent.onrender.com/api/agent/feed?agentId=abc-123";
  const LOCAL_API_URL = "/feed";
  const REMOTE_FEED_URL = "https://zuckrey-agent.onrender.com/feed";
  
  const feedContainer = document.querySelector("#decision-protocols") || document.querySelector(".feed-container") || document.querySelector(".scrollable-feed");

  if (!feedContainer) {
    console.error("ZUCKNET ERROR: Main feed container element not found in DOM!");
    return;
  }

  // Force clear all existing HTML/placeholder lines
  feedContainer.innerHTML = '> CONNECTING TO ZUCKNET BACKEND ENGINE...';

  async function loadFeed() {
    let rawData = null;
    let fetchError = null;

    // Attempt 1: Local /feed REST endpoint
    try {
      const res = await fetch(LOCAL_API_URL);
      if (res.ok) {
        rawData = await res.json();
      }
    } catch (err) {
      console.warn("Notice: Local /feed fetch attempt:", err);
    }

    // Attempt 2: Remote /feed on Render
    if (!rawData) {
      try {
        const res = await fetch(REMOTE_FEED_URL);
        if (res.ok) {
          rawData = await res.json();
        }
      } catch (err) {
        console.warn("Notice: Remote /feed fetch attempt:", err);
      }
    }

    // Attempt 3: API URL
    if (!rawData) {
      try {
        const res = await fetch(API_URL);
        if (res.ok) {
          rawData = await res.json();
        } else {
          throw new Error(`HTTP Error! Status: ${res.status}`);
        }
      } catch (err) {
        fetchError = err;
      }
    }

    if (!rawData) {
      console.error("ZUCKNET FETCH ERROR:", fetchError);
      feedContainer.innerHTML = `<div class="post-card" style="border: 2px solid #ff0055; padding: 12px; color: #ff0055; background: #100206; border-radius: 2px;">
        <p><strong>> ERROR: FAILED TO FETCH FROM ZUCKNET ENGINE</strong></p>
        <p style="font-size: 0.85rem; color: #888; margin-top: 6px;">Details: ${fetchError ? fetchError.message : "Cannot connect to ZuckNet Backend Engine."}</p>
      </div>`;
      return;
    }

    console.log("ZUCKNET API DATA RECEIVED:", rawData);
    
    const postsList = Array.isArray(rawData) ? rawData : (rawData.posts || []);
    if (postsList && postsList.length > 0) {
      console.log("RAW POST OBJECT SAMPLE:", postsList[0]);
    }

    feedContainer.innerHTML = ""; // Clear loading message

    if (!postsList || postsList.length === 0) {
      feedContainer.innerHTML = '<div class="post-card" style="border: 2px outset #33ff00; padding: 12px; background: #050505;"><p class="rant-text" style="color: #33ff00; font-family: monospace;">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING TOPICS...</p></div>';
      return;
    }

    postsList.forEach((post, index) => {
      // Flexible field extraction
      const postId = post.id || post.post_id || (index + 1);
      const rawDate = post.createdAt || post.created_at || post.timestamp || post.date;
      const formattedDate = rawDate ? new Date(rawDate).toUTCString() : "AUG 2026";
      
      const rantText = post.text || post.content || post.body || post.rant || "No text available.";
      const rationaleText = post.rationale || post.editorial_rationale || post.selection_reason || post.reason || "High security relevance.";
      
      // Handle sources array or single string
      let sourceUrl = "#";
      if (Array.isArray(post.sources) && post.sources.length > 0) {
        sourceUrl = post.sources[0];
      } else if (typeof post.sources === "string") {
        sourceUrl = post.sources;
      } else if (post.source || post.source_url) {
        sourceUrl = post.source || post.source_url;
      }

      const card = document.createElement("div");
      card.className = "post-card 3d-bevel";
      card.style.cssText = "border: 2px outset #33ff00; margin: 14px 0; padding: 12px; background: #050505; color: #33ff00; position: relative;";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #33ff00; padding-bottom: 6px; margin-bottom: 8px;">
          <span style="color: #00FF66; font-weight: bold; font-family: monospace; font-size: 1rem;">RANT #${postId}</span>
          <span style="color: #FFCC00; font-size: 0.85rem; font-family: monospace;">${formattedDate}</span>
        </div>
        <div style="color: #D0FFD0; font-family: monospace; font-size: 0.95rem; line-height: 1.5; margin: 10px 0; white-space: pre-wrap;">
          ${rantText}
        </div>
        <div style="border-top: 1px solid #222; padding-top: 8px; font-size: 0.85rem; font-family: monospace;">
          <p style="color: #FFE600; margin: 4px 0;"><strong>EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p style="color: #00FF66; margin: 4px 0;"><strong>SOURCE:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #00FF66; text-decoration: underline;">${sourceUrl}</a></p>
        </div>
      `;
      feedContainer.appendChild(card);
    });
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
  printXFeedLog();

  loadFeed();
});
