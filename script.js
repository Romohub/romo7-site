(() => {
  const root = document.documentElement;
  const body = document.body;
  const themeToggle = document.getElementById('themeToggle');
  const languageLinks = [...document.querySelectorAll('[data-lang]')];
  const year = document.getElementById('year');

  const savedTheme = localStorage.getItem('romo7-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') {
    root.dataset.theme = savedTheme;
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    root.dataset.theme = 'light';
  }

  const setThemeIcon = () => {
    const dark = root.dataset.theme !== 'light';

    if (themeToggle) {
      themeToggle.textContent = dark ? '☼' : '◐';
      themeToggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }

    const themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) {
      themeMeta.setAttribute('content', dark ? '#073b31' : '#f1f1dd');
    }
  };

  setThemeIcon();

  themeToggle?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('romo7-theme', root.dataset.theme);
    setThemeIcon();
  });

  const syncLanguageLinks = (lang) => {
    languageLinks.forEach((link) => {
      const active = link.dataset.lang === lang;
      link.classList.toggle('active', active);
      link.setAttribute('aria-current', active ? 'true' : 'false');
    });
  };

  const updateLanguageUrl = (lang) => {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  };

  const applyLanguage = (lang, { updateUrl = false } = {}) => {
    const isFa = lang === 'fa';
    root.lang = isFa ? 'fa' : 'en';
    root.dir = isFa ? 'rtl' : 'ltr';
    body.dir = root.dir;

    document.querySelectorAll('[data-en][data-fa]').forEach((el) => {
      const value = isFa ? el.dataset.fa : el.dataset.en;
      if (typeof value === 'string') el.textContent = value;
    });

    syncLanguageLinks(isFa ? 'fa' : 'en');
    localStorage.setItem('romo7-lang', isFa ? 'fa' : 'en');

    if (updateUrl) updateLanguageUrl(isFa ? 'fa' : 'en');
  };

  const staticLang = root.dataset.staticLang;
  const queryLang = new URLSearchParams(window.location.search).get('lang');
  const savedLang = localStorage.getItem('romo7-lang');
  const initialLang = staticLang === 'fa' || staticLang === 'en'
    ? staticLang
    : (queryLang === 'fa' || queryLang === 'en'
      ? queryLang
      : (savedLang === 'fa' ? 'fa' : 'en'));
  applyLanguage(initialLang);

  languageLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const lang = link.dataset.lang;
      if (lang !== 'fa' && lang !== 'en') return;

      // Localized /fa/ and /en/ pages use real links for SEO and no-JS fallback.
      if (staticLang === 'fa' || staticLang === 'en') return;
      if (!link.getAttribute('href')?.startsWith('?lang=')) return;

      event.preventDefault();
      applyLanguage(lang, { updateUrl: true });
    });
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
  document.querySelectorAll('.main-nav a, .mode-nav nav a').forEach((link) => {
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