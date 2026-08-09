/**
 * ZuckNet Y2K Terminal Boot Controller & Real-Time OS Taskbar Clock Manager
 * Non-blocking ASCII Skull Boot Sequence & Smooth 2.5s Fade Transition
 */

window.addEventListener('DOMContentLoaded', () => {
  const bootScreen = document.getElementById('boot-screen') || 
                     document.getElementById('boot-overlay') || 
                     document.querySelector('.boot-overlay') || 
                     document.querySelector('.boot-sequence');
  const mainDesktop = document.getElementById('main-desktop') || 
                      document.getElementById('main-content') || 
                      document.querySelector('.desktop-shell') || 
                      document.querySelector('.os-desktop');

  const loadingEl = document.getElementById('loading-percentage');
  const logsEl = document.getElementById('terminal-logs');

  // Ensure boot screen is visible and desktop hidden initially
  if (bootScreen) {
    bootScreen.style.display = 'flex';
    bootScreen.style.opacity = '1';
    bootScreen.style.transition = 'opacity 0.5s ease-in-out';
  }
  if (mainDesktop) {
    mainDesktop.style.display = 'none';
  }

  // Smooth terminal log progress simulation during 2.5s boot sequence
  const duration = 2000;
  const intervalTime = 40;
  const steps = duration / intervalTime;
  let currentStep = 0;

  const extraLogs = [
    '> INITIALIZING_VECTOR_MEMORY...',
    '> ESTABLISHING_SUBVERSION_PROTOCOL...',
    '> ACCESS_GRANTED.'
  ];
  let logIndex = 0;

  const bootInterval = setInterval(() => {
    currentStep++;
    const progress = Math.min(100, Math.floor((currentStep / steps) * 100));

    if (loadingEl) {
      loadingEl.textContent = `[LOADING: ${progress}%]`;
    }

    if (progress >= 30 && logIndex === 0) {
      addLogLine(extraLogs[0]);
      logIndex++;
    } else if (progress >= 65 && logIndex === 1) {
      addLogLine(extraLogs[1]);
      logIndex++;
    } else if (progress >= 90 && logIndex === 2) {
      addLogLine(extraLogs[2]);
      logIndex++;
    }

    if (currentStep >= steps) {
      clearInterval(bootInterval);
    }
  }, intervalTime);

  function addLogLine(text) {
    if (!logsEl) return;
    const line = document.createElement('div');
    line.className = 'log-line';
    line.textContent = text;
    logsEl.appendChild(line);
    logsEl.scrollTop = logsEl.scrollHeight;
  }

  // After 2.5 seconds, smoothly fade out boot screen and reveal Windows 2000 workspace
  setTimeout(() => {
    if (bootScreen) {
      bootScreen.style.opacity = '0';
      setTimeout(() => {
        bootScreen.style.display = 'none';
      }, 500); // 500ms smooth fade out
    }
    if (mainDesktop) {
      mainDesktop.style.display = 'flex';
      console.log("⚡ ZuckNet Desktop OS Workspace Revealed.");
    }
  }, 2500);

  // Tab Navigation Listeners
  const navTabs = document.querySelectorAll('.nav-tab');
  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      navTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });

  // Activate Real-Time OS Taskbar System Clock
  const clockElement = document.getElementById("taskbar-clock") || 
                       document.getElementById("os-clock") || 
                       document.querySelector(".taskbar-clock") || 
                       document.querySelector(".clock");
  if (clockElement) {
    const updateClock = () => {
      const now = new Date();
      const hh = String(now.getHours()).padStart(2, '0');
      const mm = String(now.getMinutes()).padStart(2, '0');
      const ss = String(now.getSeconds()).padStart(2, '0');
      clockElement.innerText = `${hh}:${mm}:${ss} SYS`;
    };
    updateClock();
    setInterval(updateClock, 1000);
  }
});
