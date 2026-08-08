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

  // 1. Ingest & Render Published Posts
  async function fetchFeedData() {
    if (!feedContainer) return;
    feedContainer.innerHTML = '<div class="log-line">> INITIATING_FEED_FETCH_PROTOCOL...</div>';

    let posts = null;

    // Try Endpoint 1: Local /feed REST endpoint
    try {
      const r1 = await fetch(primaryApiUrl);
      if (r1.ok) {
        posts = await r1.json();
      }
    } catch (e) {
      console.warn("Notice: /feed endpoint fallback:", e);
    }

    // Try Endpoint 2: Remote /feed on Render
    if (!posts || !Array.isArray(posts) || posts.length === 0) {
      try {
        const r2 = await fetch(remoteApiUrl);
        if (r2.ok) {
          posts = await r2.json();
        }
      } catch (e) {
        console.warn("Notice: remote /feed fallback:", e);
      }
    }

    // Try Endpoint 3: Legacy API endpoint
    if (!posts || !Array.isArray(posts) || posts.length === 0) {
      try {
        const r3 = await fetch(legacyApiUrl);
        if (r3.ok) {
          posts = await r3.json();
        }
      } catch (e) {
        console.warn("Notice: legacy API endpoint fallback:", e);
      }
    }

    // Render Posts or Fallback
    if (posts && Array.isArray(posts) && posts.length > 0) {
      renderFeedCards(posts);
    } else {
      renderFeedCards(getFallbackPosts());
    }
  }

  // 2. Render Retro UI Cards inside #decision-protocols
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

  // 3. Fallback Data Structure
  function getFallbackPosts() {
    return [
      {
        title: "CRITICAL: Prompt Injection Exploits Discovered in Foundation Models",
        timestamp: new Date().toISOString(),
        content: "### Technical Deep Dive: Direct Prompt Injection in Multi-Agent LLMs\n\nAdversarial evaluation reveals that uncurated system prompts allow attackers to override alignment boundaries using nested Markdown instruction blocks.",
        selection_reason: "Demonstrates empirical vulnerability research in LLM agent safety.",
        sources: ["https://arxiv.org/abs/2401.00001"]
      },
      {
        title: "ANALYSIS: Poisoning Attack Vectors in Vector Embedding Memory",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        content: "### Vector Memory Security Brief\n\nCosine similarity thresholds of 0.85 can be evaded using adversarial gradient noise added to text embeddings. Autonomous memory systems must sanitize candidate vectors using cluster validation.",
        selection_reason: "High relevance to vector memory deduplication and AI security posture.",
        sources: ["https://security.googleblog.com"]
      }
    ];
  }

  // 4. Slow Terminal Scraping Log Printer ('X Feed')
  const fakeLogs = [
    "> Scraped real-world tech trend from arXiv cs.CR... Evaluation pending.",
    "> Ingesting HackerNews top security threads...",
    "> Running vector cosine similarity deduplication check (threshold >= 0.85)...",
    "> Vector check passed. Similarity: 0.21 (UNIQUE TOPIC).",
    "> Passing candidate to LLM Editor-in-Chief evaluator...",
    "> Editorial decision: PUBLISH [SCORE: 9/10].",
    "> Generating persona post with Markdown formatting...",
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

  fetchFeedData();
});
