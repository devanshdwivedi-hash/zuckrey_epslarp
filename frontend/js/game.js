/**
 * ZuckNet ZUCK-RUNNER v1.0 — Arcade Endless-Runner Game Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('sidebar-game-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const W = canvas.width = 220;
  const H = canvas.height = 120;

  let state = 'IDLE';
  let score = 0;
  let highScore = 999999;
  let gameOverTimer = 0;

  const runner = {
    x: 25,
    y: 85,
    w: 14,
    h: 18,
    vy: 0,
    gravity: 0.7,
    jumpPower: -9.5,
    isJumping: false,
    groundY: 85
  };

  let obstacles = [];
  let obstacleTimer = 0;
  let gameSpeed = 3.5;

  function triggerAction() {
    if (state === 'IDLE') {
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

  function startGame() {
    state = 'PLAYING';
    score = 0;
    obstacles = [];
    obstacleTimer = 0;
    runner.y = runner.groundY;
    runner.vy = 0;
    runner.isJumping = false;
  }

  function spawnObstacle() {
    obstacleTimer++;
    if (obstacleTimer > 60 + Math.random() * 40) {
      obstacleTimer = 0;
      const isServer = Math.random() > 0.5;
      obstacles.push({
        x: W,
        y: isServer ? 80 : 85,
        w: isServer ? 14 : 10,
        h: isServer ? 22 : 18,
        type: isServer ? 'SERVER' : 'CACTUS'
      });
    }
  }

  function update() {
    if (state === 'PLAYING') {
      runner.vy += runner.gravity;
      runner.y += runner.vy;

      if (runner.y >= runner.groundY) {
        runner.y = runner.groundY;
        runner.vy = 0;
        runner.isJumping = false;
      }

      spawnObstacle();
      score += 1;

      for (let i = obstacles.length - 1; i >= 0; i--) {
        const obs = obstacles[i];
        obs.x -= gameSpeed;

        if (
          runner.x < obs.x + obs.w &&
          runner.x + runner.w > obs.x &&
          runner.y < obs.y + obs.h &&
          runner.y + runner.h > obs.y
        ) {
          triggerGameOver();
        }

        if (obs.x + obs.w < 0) {
          obstacles.splice(i, 1);
        }
      }
    } else if (state === 'GAMEOVER') {
      gameOverTimer++;
      if (gameOverTimer > 120) {
        state = 'IDLE';
      }
    }
  }

  function triggerGameOver() {
    state = 'GAMEOVER';
    gameOverTimer = 0;
    if (score > highScore) {
      highScore = score;
    }
  }

  function render() {
    ctx.fillStyle = '#040804';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = '#33ff00';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 103);
    ctx.lineTo(W, 103);
    ctx.stroke();

    if (state === 'IDLE') {
      ctx.fillStyle = '#33ff00';
      ctx.font = 'bold 11px "Courier New", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('=== ZUCK-RUNNER ===', W / 2, 28);

      if (Math.floor(Date.now() / 400) % 2 === 0) {
        ctx.fillStyle = '#00e1ff';
        ctx.fillText('INSERT COIN / PRESS SPACE', W / 2, 55);
      }

      ctx.fillStyle = '#ffb700';
      ctx.font = '10px "Courier New", monospace';
      ctx.fillText(`HI-SCORE: ${highScore}`, W / 2, 80);

      ctx.fillStyle = '#33ff00';
      ctx.fillRect(25, runner.groundY, runner.w, runner.h);

    } else if (state === 'PLAYING') {
      ctx.fillStyle = '#33ff00';
      ctx.font = 'bold 10px "Courier New", monospace';
      ctx.textAlign = 'left';
      ctx.fillText(`SCORE: ${score}`, 8, 16);
      ctx.textAlign = 'right';
      ctx.fillText(`HI: ${highScore}`, W - 8, 16);

      ctx.fillStyle = '#33ff00';
      ctx.fillRect(runner.x, runner.y, runner.w, runner.h);
      ctx.fillStyle = '#000000';
      ctx.fillRect(runner.x + 8, runner.y + 3, 5, 3);

      obstacles.forEach(obs => {
        if (obs.type === 'SERVER') {
          ctx.fillStyle = '#0e3a1e';
          ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
          ctx.strokeStyle = '#33ff00';
          ctx.lineWidth = 1;
          ctx.strokeRect(obs.x, obs.y, obs.w, obs.h);
          ctx.fillStyle = '#ff0055';
          ctx.fillRect(obs.x + 3, obs.y + 4, 3, 3);
          ctx.fillStyle = '#00ff66';
          ctx.fillRect(obs.x + 8, obs.y + 4, 3, 3);
        } else {
          ctx.fillStyle = '#22aa00';
          ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
          ctx.fillStyle = '#33ff00';
          ctx.fillRect(obs.x + 2, obs.y + 2, obs.w - 4, obs.h - 4);
        }
      });

    } else if (state === 'GAMEOVER') {
      ctx.fillStyle = '#ff0055';
      ctx.font = 'bold 11px "Courier New", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('CRASH! DATA CORRUPTED', W / 2, 48);

      ctx.fillStyle = '#ffffff';
      ctx.font = '10px "Courier New", monospace';
      ctx.fillText(`FINAL SCORE: ${score}`, W / 2, 70);
    }
  }

  function gameLoop() {
    update();
    render();
    requestAnimationFrame(gameLoop);
  }

  requestAnimationFrame(gameLoop);
});
