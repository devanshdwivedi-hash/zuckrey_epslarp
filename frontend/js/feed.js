/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Robust DOM Target & Backend Fetching Implementation
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

    try {
      const res = await fetch(LOCAL_API_URL);
      if (res.ok) {
        rawData = await res.json();
      }
    } catch (err) {
      console.warn("Notice: Local /feed fetch attempt:", err);
    }

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
    feedContainer.innerHTML = ""; // Clear loading message

    const postsList = Array.isArray(rawData) ? rawData : (rawData.posts || []);

    if (!postsList || postsList.length === 0) {
      feedContainer.innerHTML = '<div class="post-card" style="border: 2px outset #33ff00; padding: 12px; background: #050505;"><p class="rant-text" style="color: #33ff00; font-family: monospace;">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING TOPICS...</p></div>';
      return;
    }

    postsList.forEach((post, index) => {
      const card = document.createElement("div");
      card.className = "post-card 3d-bevel";
      card.style.border = "2px outset #33ff00";
      card.style.margin = "12px 0";
      card.style.padding = "12px";
      card.style.background = "#050505";
      card.style.position = "relative";

      const postId = post.id !== undefined ? post.id : (index + 1);
      const rawDate = post.createdAt || post.timestamp || post.created_at;
      const postDate = rawDate ? new Date(rawDate).toUTCString() : "TIMESTAMP_UNKNOWN";
      const rantText = post.text || post.content || post.rant || 'No text content provided.';
      const rationaleText = post.rationale || post.selection_reason || post.editorial_rationale || 'N/A';
      
      let sourceUrl = "#";
      if (Array.isArray(post.sources) && post.sources.length > 0) {
        sourceUrl = post.sources[0];
      } else if (post.source_url) {
        sourceUrl = post.source_url;
      }

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; border-bottom: 1px dashed #33ff00; padding-bottom: 6px; margin-bottom: 8px;">
          <span style="color: #00FF66; font-weight: bold; font-family: monospace;">RANT #${postId}</span>
          <span style="color: #888; font-size: 0.85rem; font-family: monospace;">${postDate}</span>
        </div>
        <div style="color: #D0FFD0; font-family: monospace; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px; white-space: pre-wrap;">
          ${rantText}
        </div>
        <div style="border-top: 1px solid #222; padding-top: 6px; font-size: 0.85rem; font-family: monospace;">
          <p style="color: #FFE600; margin: 4px 0;"><strong>EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p style="color: #00FF66; margin: 4px 0;"><strong>SOURCE:</strong> <a href="${sourceUrl}" target="_blank" rel="noopener" style="color: #00FF66; text-decoration: underline;">${sourceUrl}</a></p>
        </div>
      `;
      feedContainer.appendChild(card);
    });
  }

  loadFeed();
});
