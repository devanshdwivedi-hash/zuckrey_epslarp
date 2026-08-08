/**
 * ZuckNet Interactive Y2K Easter Eggs & Evasive Banner Ads Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  const evasiveAds = document.querySelectorAll('.evasive-ad');

  evasiveAds.forEach(ad => {
    ad.addEventListener('mousemove', (e) => {
      const offsetX = (Math.random() - 0.5) * 80;
      const offsetY = (Math.random() - 0.5) * 40;

      ad.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
      ad.style.transition = 'transform 0.1s ease-out';
    });

    ad.addEventListener('mouseleave', () => {
      setTimeout(() => {
        ad.style.transform = 'translate(0px, 0px)';
      }, 800);
    });

    ad.addEventListener('click', (e) => {
      e.preventDefault();
      alert("YOUR RAM HAS BEEN SCRAMBLED");
    });
  });

  const mp2Btn = document.getElementById('mp2-player-btn');
  const mp2Audio = document.getElementById('mp2-audio');
  let isPlaying = false;

  if (mp2Btn && mp2Audio) {
    mp2Audio.volume = 0.2;

    mp2Btn.addEventListener('click', () => {
      if (!isPlaying) {
        mp2Audio.play().then(() => {
          isPlaying = true;
          mp2Btn.classList.add('playing');
          mp2Btn.textContent = '🔊 La Fake MP2 Player [PLAYING]';
        }).catch(err => {
          isPlaying = true;
          mp2Btn.textContent = '🔊 La Fake MP2 Player [PLAYING]';
        });
      } else {
        mp2Audio.pause();
        isPlaying = false;
        mp2Btn.classList.remove('playing');
        mp2Btn.textContent = '🔈 La Fake MP2 Player [PAUSED]';
      }
    });
  }
});
