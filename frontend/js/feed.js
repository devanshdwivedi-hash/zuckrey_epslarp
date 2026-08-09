/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Dark Burgundy Deep Red Post Cards (#2b1111) & Pinkish-Grey Text (#e6d5d5)
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
      container.innerHTML = `<div class="post-card" style="background-color: #2b1111; border: 1px solid #522525; padding: 16px; display: flex; flex-direction: column; position: relative;">
        <p style="color: #ff6666; font-family: Tahoma, sans-serif; font-size: 1rem; font-weight: bold;"><strong>> ERROR: FAILED TO FETCH FROM ZUCKNET ENGINE</strong></p>
        <p style="color: #e6d5d5; font-family: Tahoma, sans-serif; font-size: 0.85rem; margin-top: 6px;">Details: ${fetchError ? fetchError.message : "Backend connection failed."}</p>
      </div>`;
      return;
    }

    const postsList = Array.isArray(rawData) ? rawData : (rawData.posts || []);

    if (!postsList || postsList.length === 0) {
      container.innerHTML = '<p style="color:#8ca68c; padding:15px; font-family:Tahoma, sans-serif; font-size:0.95rem;">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING...</p>';
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
      card.style.cssText = "background-color: #2b1111; border: 1px solid #522525; margin: 14px 0; padding: 14px; display: flex; flex-direction: column; position: relative; color: #e6d5d5; box-shadow: 0 4px 12px rgba(0,0,0,0.6);";
      
      const stampClass = (index % 2 === 0) ? 'stamp-confidential' : 'stamp-redacted';
      const stampText = (index % 2 === 0) ? 'CONFIDENTIAL' : 'REDACTED';

      card.innerHTML = `
        <span class="${stampClass}">${stampText}</span>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #522525; padding-bottom: 8px; margin-bottom: 12px; padding-right: 110px;">
          <span style="color: #ff6666; font-weight: bold; font-family: Tahoma, sans-serif; font-size: 1rem; letter-spacing: 0.5px; text-transform: uppercase;">RANT #${postId}</span>
          <span style="color: #e0b65c; font-size: 0.85rem; font-family: Tahoma, monospace;">${formattedDate}</span>
        </div>
        
        <!-- PINKISH-GREY BODY TEXT (#e6d5d5) -->
        <div class="post-content" style="color: #e6d5d5; font-family: Tahoma, sans-serif; font-size: 0.95rem; line-height: 1.5; text-shadow: 0 0 2px rgba(0,0,0,1); display: block; white-space: pre-wrap; margin-bottom: 14px;">${mainText}</div>
        
        <div style="border-top: 1px solid #522525; padding-top: 8px; font-size: 0.85rem; font-family: Tahoma, sans-serif;">
          <p style="color: #8ca68c; margin: 4px 0; line-height: 1.4;"><strong>> EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p style="color: #b3b3b3; margin: 4px 0;"><strong>> SOURCE LINK:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #33ff00; text-decoration: underline; background: #1a0a0a; padding: 2px 4px;">[VIEW SOURCE]</a></p>
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
