(() => {
  const root = document.documentElement;
  const body = document.body;
  const themeToggle = document.getElementById('themeToggle');
  const langToggle = document.getElementById('langToggle');
  const year = document.getElementById('year');

  const savedTheme = localStorage.getItem('romo7-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') {
    root.dataset.theme = savedTheme;
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    root.dataset.theme = 'light';
  }

  const setThemeIcon = () => {
    if (!themeToggle) return;
    const dark = root.dataset.theme !== 'light';
    themeToggle.textContent = dark ? '☼' : '◐';
    themeToggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
  };

  setThemeIcon();

  themeToggle?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('romo7-theme', root.dataset.theme);
    setThemeIcon();
  });

  const applyLanguage = (lang) => {
    const isFa = lang === 'fa';
    root.lang = isFa ? 'fa' : 'en';
    root.dir = isFa ? 'rtl' : 'ltr';
    body.dir = root.dir;

    document.querySelectorAll('[data-en][data-fa]').forEach((el) => {
      const value = isFa ? el.dataset.fa : el.dataset.en;
      if (typeof value === 'string') el.textContent = value;
    });

    if (langToggle) {
      langToggle.textContent = isFa ? 'EN' : 'FA';
      langToggle.setAttribute('aria-label', isFa ? 'Switch to English' : 'تغییر به فارسی');
    }

    localStorage.setItem('romo7-lang', isFa ? 'fa' : 'en');
  };

  const savedLang = localStorage.getItem('romo7-lang');
  applyLanguage(savedLang === 'fa' ? 'fa' : 'en');

  langToggle?.addEventListener('click', () => {
    applyLanguage(root.lang === 'fa' ? 'en' : 'fa');
  });

  if (year) year.textContent = new Date().getFullYear();

  const revealItems = [...document.querySelectorAll('.reveal')];
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('visible'));
  }

  const current = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach((link) => {
    const href = (link.getAttribute('href') || '').split('#')[0];
    if (href && href === current) link.classList.add('active');
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (event) => {
      const id = link.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
})();