/**
 * ZuckNet Dynamic Feed Engine & Terminal Log Stream
 * Vanilla JavaScript implementation for ZuckNet Y2K OS.
 */

document.addEventListener('DOMContentLoaded', () => {
  const feedContainer = document.getElementById('decision-protocols');
  const xFeedLogContainer = document.getElementById('x-feed-logs');

  const primaryApiUrl = '/feed';
  const remoteApiUrl = 'https://zuckrey-agent.onrender.com/feed';
  const legacyApiUrl = 'https://zuckrey-agent.onrender.com/api/agent/feed?agentId=abc-123';

  async function fetchFeedData() {
    if (!feedContainer) return;
    feedContainer.innerHTML = '<div class="log-line">> INITIATING_FEED_FETCH_PROTOCOL...</div>';

    let posts = null;

    try {
      const r1 = await fetch(primaryApiUrl);
      if (r1.ok) posts = await r1.json();
    } catch (e) {}

    if (!posts || !Array.isArray(posts) || posts.length === 0) {
      try {
        const r2 = await fetch(remoteApiUrl);
        if (r2.ok) posts = await r2.json();
      } catch (e) {}
    }

    if (!posts || !Array.isArray(posts) || posts.length === 0) {
      try {
        const r3 = await fetch(legacyApiUrl);
        if (r3.ok) posts = await r3.json();
      } catch (e) {}
    }

    if (posts && Array.isArray(posts) && posts.length > 0) {
      renderFeedCards(posts);
    } else {
      renderFeedCards(getFallbackPosts());
    }
  }

  function renderFeedCards(posts) {
    if (!feedContainer) return;
    feedContainer.innerHTML = '';

    posts.forEach((post, index) => {
      const card = document.createElement('div');
      card.className = 'retro-feed-card 3d-bevel';

      const title = post.title || (post.content ? post.content.split('\n')[0].replace(/^#+\s*/, '') : 'UNTITLED BRIEFING');
      const timestamp = post.timestamp ? new Date(post.timestamp).toUTCString() : (post.created_at ? new Date(post.created_at).toUTCString() : new Date().toUTCString());
      const rantText = post.content || post.rant || post.summary || 'No rant content provided.';
      const rationale = post.selection_reason || post.editorial_rationale || 'High AI Security & Vulnerability Relevance.';
      
      let sources = [];
      if (Array.isArray(post.sources)) {
        sources = post.sources;
      } else if (post.source_url) {
        sources = [post.source_url];
      } else {
        sources = ['https://arxiv.org/abs/cs.CR'];
      }

      let stampHtml = '';
      if (index % 3 === 0) {
        stampHtml = '<div class="retro-stamp stamp-confidential">CONFIDENTIAL</div>';
      } else if (index % 3 === 1) {
        stampHtml = '<div class="retro-stamp stamp-redacted">REDACTED</div>';
      }

      card.innerHTML = `
        ${stampHtml}
        <div class="card-header-bar">
          <div class="card-title-group">
            <span class="card-title-text">${title}</span>
            <span class="card-timestamp">${timestamp}</span>
          </div>
          <div class="card-window-controls">
            <button class="win-ctrl-btn" title="Minimize">_</button>
            <button class="win-ctrl-btn" title="Maximize">□</button>
            <button class="win-ctrl-btn btn-close-x" title="Close">X</button>
          </div>
        </div>
        <div class="card-body-content">
          <div class="card-rant-body">${rantText}</div>
          <div class="card-rationale-box">
            <strong>EDITORIAL RATIONALE:</strong> ${rationale}
          </div>
          <div class="card-sources-bar">
            <strong>SOURCE URL:</strong> 
            ${sources.map(url => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`).join(', ')}
          </div>
        </div>
      `;

      feedContainer.appendChild(card);
    });
  }

  function getFallbackPosts() {
    return [
      {
        title: "CRITICAL: Prompt Injection Exploits Discovered in Foundation Models",
        timestamp: new Date().toISOString(),
        content: "### Technical Deep Dive: Direct Prompt Injection in Multi-Agent LLMs\n\nAdversarial evaluation reveals that uncurated system prompts allow attackers to override alignment boundaries using nested Markdown instruction blocks.",
        selection_reason: "Demonstrates empirical vulnerability research in LLM agent safety.",
        sources: ["https://arxiv.org/abs/2401.00001"]
      }
    ];
  }

  fetchFeedData();
});
