/* =========================================================
   SD-Guide — shared scripts for all pages
   - Language toggle (English / Chinese)
   - Theme toggle (dark / light)
   - Active nav highlight
   - Helper: renderMermaid
   ========================================================= */

(function () {
  'use strict';

  // ---------- Language handling ----------
  const LANG_KEY = 'sdguide.lang';
  const THEME_KEY = 'sdguide.theme';

  function getLang() {
    try { return localStorage.getItem(LANG_KEY) || 'en'; }
    catch (e) { return 'en'; }
  }

  function setLang(lang) {
    try { localStorage.setItem(LANG_KEY, lang); } catch (e) {}
    document.documentElement.setAttribute('lang', lang);
    updateLangButton(lang);
  }

  function updateLangButton(lang) {
    const btn = document.getElementById('lang-toggle');
    if (btn) {
      btn.textContent = lang === 'en' ? '中文' : 'EN';
      btn.setAttribute('aria-label', lang === 'en' ? 'Switch to Chinese' : 'Switch to English');
    }
  }

  function toggleLang() {
    const next = getLang() === 'en' ? 'zh' : 'en';
    setLang(next);
  }

  // ---------- Theme handling ----------
  function getTheme() {
    try { return localStorage.getItem(THEME_KEY) || 'dark'; }
    catch (e) { return 'dark'; }
  }

  function setTheme(theme) {
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) {}
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeButton(theme);
  }

  function updateThemeButton(theme) {
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? '☀' : '☾';
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    }
  }

  function toggleTheme() {
    const next = getTheme() === 'dark' ? 'light' : 'dark';
    setTheme(next);
    // Re-render Mermaid diagrams with the new theme
    if (window.mermaid && document.querySelectorAll('.mermaid').length) {
      setTimeout(() => { try { reinitMermaid(); } catch (e) {} }, 50);
    }
  }

  // ---------- Active nav ----------
  function markActiveNav() {
    const path = location.pathname.replace(/\\/g, '/');
    document.querySelectorAll('.nav-links a').forEach((a) => {
      const href = a.getAttribute('href');
      if (!href || href === '#') return;
      // Match section: /arena, /guide, /resources, /about
      if (a.dataset.match) {
        if (path.includes(a.dataset.match)) a.classList.add('active');
      } else if (path.endsWith('index.html') && (href === './' || href === 'index.html')) {
        a.classList.add('active');
      }
    });
  }

  // ---------- Mermaid ----------
  function reinitMermaid() {
    if (!window.mermaid) return;
    const isDark = getTheme() === 'dark';
    window.mermaid.initialize({
      startOnLoad: false,
      theme: isDark ? 'dark' : 'default',
      themeVariables: isDark ? {
        darkMode: true,
        background: '#1a1a22',
        primaryColor: '#22222c',
        primaryTextColor: '#e6e6ec',
        primaryBorderColor: '#2a2a36',
        lineColor: '#6b6b78',
        secondaryColor: '#14141a',
        tertiaryColor: '#14141a',
        fontFamily: 'inherit',
      } : {
        fontFamily: 'inherit',
      },
      securityLevel: 'loose',
    });
    // Re-run on all .mermaid nodes
    document.querySelectorAll('.mermaid').forEach((el, i) => {
      // If we've already rendered, reset so it re-renders fresh
      const src = el.getAttribute('data-source');
      if (src) {
        el.textContent = src;
        el.removeAttribute('data-processed');
      } else {
        el.setAttribute('data-source', el.textContent);
      }
    });
    window.mermaid.run({ querySelector: '.mermaid' }).catch(() => {});
  }

  // ---------- Company carousel (landing page) ----------
  function initCompanyStage() {
    const stage = document.querySelector('.company-stage');
    if (!stage) return;
    const slides = Array.from(stage.querySelectorAll('.company-slide'));
    const dots = Array.from(stage.querySelectorAll('.company-stage-dots button'));
    const prev = stage.querySelector('.company-stage-nav.prev');
    const next = stage.querySelector('.company-stage-nav.next');
    if (slides.length < 2) return;

    let idx = Math.max(0, slides.findIndex((s) => s.classList.contains('is-active')));
    const autoplayMs = parseInt(stage.dataset.autoplay || '0', 10);
    let timer = null;

    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach((s, j) => s.classList.toggle('is-active', j === idx));
      dots.forEach((d, j) => d.classList.toggle('is-active', j === idx));
    }
    function startAutoplay() {
      stopAutoplay();
      if (autoplayMs > 0) timer = setInterval(() => show(idx + 1), autoplayMs);
    }
    function stopAutoplay() { if (timer) { clearInterval(timer); timer = null; } }

    if (prev) prev.addEventListener('click', (e) => { e.preventDefault(); show(idx - 1); startAutoplay(); });
    if (next) next.addEventListener('click', (e) => { e.preventDefault(); show(idx + 1); startAutoplay(); });
    dots.forEach((d, i) => d.addEventListener('click', (e) => { e.preventDefault(); show(i); startAutoplay(); }));

    stage.addEventListener('mouseenter', stopAutoplay);
    stage.addEventListener('mouseleave', startAutoplay);

    startAutoplay();
  }

  // ---------- Init ----------
  function init() {
    // Apply stored language & theme ASAP
    setLang(getLang());
    setTheme(getTheme());

    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) langBtn.addEventListener('click', toggleLang);

    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    markActiveNav();
    initCompanyStage();

    // Initial mermaid render
    if (window.mermaid && document.querySelectorAll('.mermaid').length) {
      reinitMermaid();
    }
  }

  // Run before DOM ready: set theme/lang on <html> to avoid flash
  try {
    document.documentElement.setAttribute('lang', getLang());
    document.documentElement.setAttribute('data-theme', getTheme());
  } catch (e) {}

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // ---------- Arena filtering (used only on arena index page) ----------
  window.SDArena = {
    init(allTags) {
      const list = document.getElementById('question-list');
      if (!list) return;

      const cards = Array.from(list.querySelectorAll('.question-card'));
      const searchInput = document.getElementById('arena-search');
      const chipsContainer = document.getElementById('filter-chips');
      const countEl = document.getElementById('result-count');

      const state = {
        search: '',
        company: 'all',
        category: 'all',
      };

      function applyFilters() {
        const s = state.search.toLowerCase();
        let visible = 0;
        cards.forEach((card) => {
          const matchesSearch = !s ||
            card.textContent.toLowerCase().includes(s) ||
            (card.dataset.search && card.dataset.search.toLowerCase().includes(s));
          const matchesCompany = state.company === 'all' || card.dataset.company === state.company;
          const matchesCategory = state.category === 'all' ||
            (card.dataset.categories || '').split(',').includes(state.category);

          const show = matchesSearch && matchesCompany && matchesCategory;
          card.style.display = show ? '' : 'none';
          if (show) visible++;
        });
        if (countEl) countEl.textContent = visible;
      }

      if (searchInput) {
        searchInput.addEventListener('input', (e) => {
          state.search = e.target.value;
          applyFilters();
        });
      }

      if (chipsContainer) {
        chipsContainer.addEventListener('click', (e) => {
          const chip = e.target.closest('.filter-chip');
          if (!chip) return;
          const group = chip.dataset.group;
          const value = chip.dataset.value;
          // Clear siblings
          chipsContainer.querySelectorAll(`[data-group="${group}"]`).forEach((c) => c.classList.remove('active'));
          chip.classList.add('active');
          state[group] = value;
          applyFilters();
        });
      }

      // Pre-filter from ?company= URL param (used by the landing-page carousel)
      const params = new URLSearchParams(location.search);
      const initialCompany = params.get('company');
      if (initialCompany && ['openai', 'anthropic', 'google', 'xai'].includes(initialCompany) && chipsContainer) {
        const match = chipsContainer.querySelector(`[data-group="company"][data-value="${initialCompany}"]`);
        if (match) {
          chipsContainer.querySelectorAll('[data-group="company"]').forEach((c) => c.classList.remove('active'));
          match.classList.add('active');
          state.company = initialCompany;
        }
      }

      applyFilters();
    }
  };
})();
