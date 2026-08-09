/**
 * ZuckNet ZUCK-RUNNER v1.0 — Bitmap Sprite Endless-Runner Game Engine
 * Player: Zuckrey Raptor (assets/img/zuckrey_raptor.png)
 * Obstacle: Matrix Cactus (assets/img/cactus_obstacle.png)
 * Background: Matrix Desert (assets/img/matrix_desert_bg.png)
 * Shorter Cactus (25x35), Enhanced Jump Physics (-12.0), Padded Hitbox (5px)
 */

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('sidebar-game-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  // Hardcoded static 300x150 internal resolution
  const W = canvas.width = 300;
  const H = canvas.height = 150;
  const groundLineY = 135; // Matrix floor line Y coordinate

  // 1. Load Image Assets
  const playerImg = new Image();
  playerImg.src = 'assets/img/zuckrey_raptor.png';

  const obstacleImg = new Image();
  obstacleImg.src = 'assets/img/cactus_obstacle.png';

  const bgImg = new Image();
  bgImg.src = 'assets/img/matrix_desert_bg.png';

  // Game States: 'IDLE', 'PLAYING', 'GAMEOVER'
  let state = 'IDLE';
  let score = 0;
  let cactiJumped = 0;
  let gameOverTimer = 0;

  // Player Character (Zuckrey Raptor: 60px x 60px)
  // Feet sit flush on ground line: groundY = 135 - 60 = 75
  const playerWidth = 60;
  const playerHeight = 60;
  const runner = {
    x: 20,
    y: groundLineY - playerHeight,
    w: playerWidth,
    h: playerHeight,
    vy: 0,
    gravity: 0.65,
    jumpPower: -12.0, // Increased vertical jump air time
    isJumping: false,
    groundY: groundLineY - playerHeight
  };

  // Shorter Shrunken Obstacles (Cactus: 25px x 35px)
  // Bottom sits flush on ground line: y = 135 - 35 = 100
  const obstacleWidth = 25;
  const obstacleHeight = 35;
  let obstacles = [];
  let obstacleTimer = 0;

  // Throttled Game Speed (reduced by 30% to 2.5 for smooth, readable gameplay)
  let gameSpeed = 2.5;

  // Action / Jump Trigger
  function triggerAction() {
    if (state === 'IDLE' || state === 'GAMEOVER') {
      startGame();
    } else if (state === 'PLAYING') {
      if (!runner.isJumping) {
        runner.vy = runner.jumpPower;
        runner.isJumping = true;
      }
    }
  }

  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
      e.preventDefault();
      triggerAction();
    }
  });

  canvas.addEventListener('mousedown', (e) => {
    e.preventDefault();
    triggerAction();
  });

  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    triggerAction();
  });

  function startGame() {
    state = 'PLAYING';
    score = 0;
    cactiJumped = 0;
    obstacles = [];
    obstacleTimer = 0;
    runner.y = runner.groundY;
    runner.vy = 0;
    runner.isJumping = false;
  }

  function spawnObstacle() {
    obstacleTimer++;
    if (obstacleTimer > 65 + Math.random() * 40) {
      obstacleTimer = 0;
      obstacles.push({
        x: W,
        y: groundLineY - obstacleHeight, // Flush at y = 100
        w: obstacleWidth,
        h: obstacleHeight,
        passed: false
      });
    }
  }

  function update() {
    if (state === 'PLAYING') {
      // Runner Physics
      runner.vy += runner.gravity;
      runner.y += runner.vy;

      if (runner.y >= runner.groundY) {
        runner.y = runner.groundY;
        runner.vy = 0;
        runner.isJumping = false;
      }

      // Obstacles Physics
      spawnObstacle();
      score += 1;

      for (let i = obstacles.length - 1; i >= 0; i--) {
        const obs = obstacles[i];
        obs.x -= gameSpeed;

        // Count Cacti Jumped
        if (!obs.passed && obs.x + obs.w < runner.x) {
          obs.passed = true;
          cactiJumped++;
        }

        // Forgiving Padded Hitbox Collision Detection
        const pLeft = runner.x + 15;
        const pRight = (runner.x + runner.w) - 15;
        const pTop = runner.y + 15;
        const pBottom = runner.y + runner.h; // Keep bottom flush with feet

        const oLeft = obs.x + 5;
        const oRight = (obs.x + obs.w) - 5;
        const oTop = obs.y + 5;
        const oBottom = obs.y + obs.h;

        if (pLeft < oRight && pRight > oLeft && pTop < oBottom && pBottom > oTop) {
          triggerGameOver();
        }

        if (obs.x + obs.w < 0) {
          obstacles.splice(i, 1);
        }
      }
    } else if (state === 'GAMEOVER') {
      gameOverTimer++;
      if (gameOverTimer > 180) {
        state = 'IDLE';
      }
    }
  }

  function triggerGameOver() {
    state = 'GAMEOVER';
    gameOverTimer = 0;
  }

  // Update HUD score overlay at top of canvas
  function drawHUD() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
    ctx.fillRect(0, 0, W, 44);

    ctx.font = 'bold 9px "Courier New", monospace';
    ctx.textAlign = 'left';

    // HIGH SCORE: [GLITCHING] 9,999,999,999 (Zuckrey AI)
    ctx.fillStyle = '#ff6666';
    ctx.fillText('HIGH SCORE: [GLITCHING] 9,999,999,999 (Zuckrey AI)', 6, 12);

    // CURRENT SCORE: <active_score> (Zuckrey Raptor)
    ctx.fillStyle = '#33ff00';
    ctx.fillText(`CURRENT SCORE: ${score} (Zuckrey Raptor)`, 6, 25);

    // CACTI JUMPED: <count>
    ctx.fillStyle = '#ffff55';
    ctx.fillText(`CACTI JUMPED: ${cactiJumped}`, 6, 38);
  }

  // Main draw() loop with bitmap sprites & background
  function draw() {
    // 1. Draw background image covering full canvas width and height
    if (bgImg.complete && bgImg.naturalWidth !== 0) {
      ctx.drawImage(bgImg, 0, 0, W, H);
    } else {
      ctx.fillStyle = '#040804';
      ctx.fillRect(0, 0, W, H);
    }

    // Ground Line (Matrix Floor)
    ctx.strokeStyle = '#33ff00';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, groundLineY);
    ctx.lineTo(W, groundLineY);
    ctx.stroke();

    // 2. Draw playerImg at player's current (x, y) coordinates
    if (playerImg.complete && playerImg.naturalWidth !== 0) {
      ctx.drawImage(playerImg, runner.x, runner.y, runner.w, runner.h);
    } else {
      ctx.fillStyle = '#33ff00';
      ctx.fillRect(runner.x, runner.y, runner.w, runner.h);
    }

    // 3. Draw shrunken obstacleImg at each obstacle's (x, y) location
    obstacles.forEach(obs => {
      if (obstacleImg.complete && obstacleImg.naturalWidth !== 0) {
        ctx.drawImage(obstacleImg, obs.x, obs.y, obs.w, obs.h);
      } else {
        ctx.fillStyle = '#22aa00';
        ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
      }
    });

    // 4. Draw HUD Overlay
    drawHUD();

    // Overlays for IDLE & GAMEOVER
    if (state === 'IDLE') {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
      ctx.fillRect(0, 50, W, 40);

      ctx.fillStyle = '#33ff00';
      ctx.font = 'bold 11px "Courier New", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('=== ZUCK-RUNNER ===', W / 2, 65);

      if (Math.floor(Date.now() / 400) % 2 === 0) {
        ctx.fillStyle = '#00e1ff';
        ctx.font = 'bold 9px "Courier New", monospace';
        ctx.fillText('CLICK / PRESS SPACE TO START', W / 2, 80);
      }
    } else if (state === 'GAMEOVER') {
      ctx.fillStyle = 'rgba(30, 0, 0, 0.85)';
      ctx.fillRect(0, 50, W, 40);

      ctx.fillStyle = '#ff0055';
      ctx.font = 'bold 11px "Courier New", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('CRASH! RAPTOR WIPEOUT', W / 2, 65);

      ctx.fillStyle = '#ffffff';
      ctx.font = '9px "Courier New", monospace';
      ctx.fillText('CLICK / PRESS SPACE TO RESTART', W / 2, 80);
    }
  }

  // Master Loop
  function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
  }

  requestAnimationFrame(gameLoop);
});
