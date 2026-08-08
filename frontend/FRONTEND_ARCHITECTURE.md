# 🕹️ Zuckrey EpsLarp Bunker OS — Frontend Architecture Specification

## Overview
The **Zuckrey EpsLarp Digital Bunker OS** is a paranoid, Y2K retro-cyberpunk desktop interface designed to present autonomous AI research briefings, live system telemetry, interactive mini-games, and security logs in an immersive 1999-era OS window environment.

---

## 📂 Directory Structure
```text
frontend/
├── index.html                  # Single-page OS entry point & structural shell
├── FRONTEND_ARCHITECTURE.md    # Master architecture blueprint
├── styles/
│   ├── variables.css           # Global theme variables (colors, fonts, z-indices)
│   ├── main.css                # Base OS windows, taskbar, layout grid, typography
│   └── crt.css                 # Screen curvature, scanlines, bloom, and vignette filters
├── js/
│   ├── app.js                  # Master controller, OS boot sequence, tab router
│   ├── feed.js                 # API data layer, JSON parser, card renderer, log stream
│   ├── game.js                 # 2D Canvas engine, physics loop, collision detection
│   └── popups.js               # Event-driven chaos, cursor tracking, retro modals
└── assets/
    ├── img/                    # Pixel art icons, avatars, scam banner ads
    └── audio/                  # Retro ambient hums, dial-up sounds
```

---

## 🎨 Design System & Visual Aesthetic
1. **Retro CRT Display Effects**:
   - Scanline overlays, phosphor screen flicker, CRT curvature, and green/amber monospaced typography.
2. **Window Management Interface**:
   - Retro Win95/Cyberpunk desktop windows with titlebars, minimize/maximize buttons, and draggable z-index layering.
3. **Data Layer (`feed.js`)**:
   - Consumes live `/feed` REST API endpoint from backend.
   - Formats Markdown post content, editorial selection rationales, and source URLs.
4. **Interactive Arcade Engine (`game.js`)**:
   - 2D HTML5 Canvas mini-game ("Bunker Evasion") with player controls, score loop, and collision detection.
5. **Popups & System Alerts (`popups.js`)**:
   - Event-driven system warnings, paranoid terminal alerts, and interactive retro modals.
