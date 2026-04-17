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

      applyFilters();
    }
  };
})();
