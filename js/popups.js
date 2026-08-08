/**
 * ZuckNet Interactive Y2K Easter Eggs & Evasive Banner Ads Engine
 * Vanilla JavaScript implementation.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Evasive Banner Ads Logic ("DOWNLOAD MORE RAM")
  const evasiveAds = document.querySelectorAll('.evasive-ad');

  evasiveAds.forEach(ad => {
    // Evade cursor on hover / mousemove
    ad.addEventListener('mousemove', (e) => {
      const rect = ad.getBoundingClientRect();
      const offsetX = (Math.random() - 0.5) * 80;
      const offsetY = (Math.random() - 0.5) * 40;

      ad.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
      ad.style.transition = 'transform 0.1s ease-out';
    });

    // Reset position when cursor leaves
    ad.addEventListener('mouseleave', () => {
      setTimeout(() => {
        ad.style.transform = 'translate(0px, 0px)';
      }, 800);
    });

    // Alert if user manages to click the ad
    ad.addEventListener('click', (e) => {
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
