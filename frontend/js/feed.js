/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Vanilla JavaScript implementation for ZuckNet Y2K OS.
 */

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('decision-protocols');
  const xFeedLogContainer = document.getElementById('x-feed-logs');

  const primaryApiUrl = '/feed';
  const remoteApiUrl = 'https://zuckrey-agent.onrender.com/feed';
  const legacyApiUrl = 'https://zuckrey-agent.onrender.com/api/agent/feed?agentId=abc-123';

  async function fetchFeedData() {
    if (!container) return;
    
    // Explicitly wipe out all static content and placeholder lines
    container.innerHTML = '<p class="feed-status">> INITIATING_FEED_FETCH_PROTOCOL...</p>';

    let posts = null;

    try {
      const r1 = await fetch(primaryApiUrl);
      if (r1.ok) {
        const data = await r1.json();
        posts = Array.isArray(data) ? data : (data.posts || null);
      }
    } catch (e) {
      console.warn("Notice: /feed fetch failed, trying remote:", e);
    }

    if (!posts || !Array.isArray(posts) || posts.length === 0) {
      try {
        const r2 = await fetch(remoteApiUrl);
        if (r2.ok) {
          const data = await r2.json();
          posts = Array.isArray(data) ? data : (data.posts || null);
        }
      } catch (e) {
        console.warn("Notice: Remote /feed fetch failed, trying legacy:", e);
      }
    }

    if (!posts || !Array.isArray(posts) || posts.length === 0) {
      try {
        const r3 = await fetch(legacyApiUrl);
        if (r3.ok) {
          const data = await r3.json();
          posts = Array.isArray(data) ? data : (data.posts || null);
        }
      } catch (e) {
        console.warn("Notice: Legacy API endpoint fetch failed:", e);
      }
    }

    container.innerHTML = "";

    if (posts && Array.isArray(posts) && posts.length > 0) {
      renderFeedCards(posts);
    } else if (posts && Array.isArray(posts) && posts.length === 0) {
      container.innerHTML = '<p class="feed-status">> NO RANTS PUBLISHED YET. AUTONOMOUS LOOP EVALUATING...</p>';
    } else {
      container.innerHTML = '<p class="feed-error">> ERROR: CANNOT CONNECT TO ZUCKNET BACKEND ENGINE</p>';
    }
  }

  function renderFeedCards(posts) {
    if (!container) return;
    container.innerHTML = "";

    posts.forEach((post, index) => {
      const postId = post.id !== undefined ? post.id : (index + 1);
      const createdAtRaw = post.createdAt || post.timestamp || post.created_at || new Date().toISOString();
      const formattedDate = new Date(createdAtRaw).toUTCString();
      const rantText = post.text || post.content || post.rant || 'No text content available.';
      const rationaleText = post.rationale || post.selection_reason || post.editorial_rationale || 'High AI Vulnerability & Vector Security Relevance.';

      let sourceList = [];
      if (Array.isArray(post.sources) && post.sources.length > 0) {
        sourceList = post.sources;
      } else if (post.source_url) {
        sourceList = [post.source_url];
      } else {
        sourceList = ['https://arxiv.org/abs/cs.CR'];
      }
      const primarySource = sourceList[0];

      const stampClass = (index % 2 === 0) ? 'stamp-confidential' : 'stamp-redacted';
      const stampText = (index % 2 === 0) ? 'CONFIDENTIAL' : 'REDACTED';

      const card = document.createElement("div");
      card.className = "post-card 3d-bevel";
      card.innerHTML = `
        <div class="card-header">
          <span class="post-title">RANT #${postId}</span>
          <span class="post-date">${formattedDate}</span>
          <span class="${stampClass}">${stampText}</span>
        </div>
        <div class="card-body">
          <p class="rant-text">${rantText}</p>
        </div>
        <div class="card-footer">
          <p class="rationale"><strong>EDITORIAL RATIONALE:</strong> ${rationaleText}</p>
          <p class="sources"><strong>SOURCE:</strong> <a href="${primarySource}" target="_blank" rel="noopener noreferrer">${primarySource}</a></p>
        </div>
      `;

      container.appendChild(card);
    });
  }

  fetchFeedData();
});
