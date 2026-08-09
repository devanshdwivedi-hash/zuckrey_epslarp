/**
 * ZuckNet Interactive Y2K Easter Eggs & Evasive Banner Ads Engine
 * Vanilla JavaScript implementation.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Evasive Banner Ads & Fleeing Ad Boxes Logic
  const evasiveBoxes = document.querySelectorAll('.fleeing-ad-box, .evasive-ad, .fleeing-ad');

  evasiveBoxes.forEach(box => {
    // Evade cursor on hover / mouseover
    box.addEventListener('mouseover', () => {
      const randomX = (Math.random() - 0.5) * 300;
      const randomY = (Math.random() - 0.5) * 200;
      box.style.transform = `translate(${randomX}px, ${randomY}px) scale(0.9)`;
      box.style.transition = 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease-in-out';
    });

    // Reset position when cursor leaves
    box.addEventListener('mouseleave', () => {
      setTimeout(() => {
        box.style.transform = 'translate(0px, 0px) scale(1)';
      }, 1000);
    });

    // Alert if user manages to click the ad
    box.addEventListener('click', (e) => {
      e.preventDefault();
      alert("YOUR RAM HAS BEEN SCRAMBLED");
    });
  });

  // 2. 'La Fake MP2 Player' Taskbar Functional Audio Toggle
  const mp2Btn = document.getElementById('mp2-player-btn');
  const mp2Audio = document.getElementById('mp2-audio');
  let isPlaying = false;

  if (mp2Btn && mp2Audio) {
    mp2Audio.volume = 0.2; // Low-volume dreary ambient track

    mp2Btn.addEventListener('click', () => {
      if (!isPlaying) {
        mp2Audio.play().then(() => {
          isPlaying = true;
          mp2Btn.classList.add('playing');
          mp2Btn.textContent = '🔊 La Fake MP2 Player [PLAYING]';
          console.log("🎵 La Fake MP2 Player: Playing ambient synth track.");
        }).catch(err => {
          console.warn("Audio playback notice:", err);
          // Fallback toggle state if browser restricts autoplay without interaction
          isPlaying = true;
          mp2Btn.textContent = '🔊 La Fake MP2 Player [PLAYING]';
        });
      } else {
        mp2Audio.pause();
        isPlaying = false;
        mp2Btn.classList.remove('playing');
        mp2Btn.textContent = '🔈 La Fake MP2 Player [PAUSED]';
        console.log("⏸️ La Fake MP2 Player: Paused.");
      }
    });
  }
});
