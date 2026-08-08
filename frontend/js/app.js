/**
 * ZuckNet Y2K Terminal Boot Controller & Desktop OS Manager
 */

document.addEventListener('DOMContentLoaded', () => {
  const bootScreen = document.getElementById('boot-screen');
  const mainContent = document.getElementById('main-content');
  const loadingEl = document.getElementById('loading-percentage');
  const logsEl = document.getElementById('terminal-logs');
  const clockEl = document.getElementById('taskbar-clock');

  const duration = 3000;
  const intervalTime = 30;
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

    if (progress >= 35 && logIndex === 0) {
      addLogLine(extraLogs[0]);
      logIndex++;
    } else if (progress >= 70 && logIndex === 1) {
      addLogLine(extraLogs[1]);
      logIndex++;
    } else if (progress >= 95 && logIndex === 2) {
      addLogLine(extraLogs[2]);
      logIndex++;
    }

    if (currentStep >= steps) {
      clearInterval(bootInterval);

      setTimeout(() => {
        if (bootScreen) bootScreen.style.display = 'none';
        if (mainContent) mainContent.style.display = 'flex';
        console.log("⚡ ZuckNet Desktop OS Initialized.");
      }, 200);
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

  const navTabs = document.querySelectorAll('.nav-tab');
  navTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      navTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    });
  });

  if (clockEl) {
    const updateClock = () => {
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString();
    };
    updateClock();
    setInterval(updateClock, 1000);
  }
});
