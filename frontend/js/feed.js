/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Aggressive Y2K Terminal Timestamp Extraction & 30-Second Polling Loop
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
      card.className = "post-card 3d-bevel";
      card.style.cssText = "border: 2px outset #33ff00; margin: 16px 0; padding: 16px; background-color: #050505; display: block; visibility: visible; height: auto; overflow: visible; position: relative;";

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; border-bottom: 2px dashed #115511; padding-bottom: 8px; margin-bottom: 12px;">
          <span style="color: #00FF66; font-weight: bold; font-family: 'Courier New', monospace; font-size: 1.1rem; text-transform: uppercase;">RANT #${postId}</span>
          <span style="color: #FFCC00; font-size: 0.95rem; font-family: 'Courier New', monospace; letter-spacing: 1px; text-shadow: 0 0 5px #FFCC00;">${formattedDate}</span>
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

document.addEventListener("DOMContentLoaded", () => {
  fetchFeed();
  setInterval(fetchFeed, 30000);
});
