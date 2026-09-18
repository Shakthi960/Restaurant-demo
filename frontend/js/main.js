/* ==========================================================================
   GALAXY RESTAURANTS — main.js
   Shared helpers & bootstrapping. DOM is ready.
   ========================================================================== */

(function () {
  'use strict';

  /* ---------- Utility ---------- */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  window.Galaxy = window.Galaxy || { $: $, $$: $$ };

  /* ---------- Brand splash (plays once per session) ---------- */
  const splash = document.getElementById('splash');

  if (splash) {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const alreadySeen = sessionStorage.getItem('galaxy-splash');

    if (reduceMotion || alreadySeen) {
      splash.remove();
    } else {
      sessionStorage.setItem('galaxy-splash', '1');
      document.body.classList.add('splash-lock');

      function dismissSplash() {
        splash.classList.add('is-leaving');
      }

      if (document.readyState === 'complete') {
        setTimeout(dismissSplash, 3900);
      } else {
        window.addEventListener('load', function () {
          setTimeout(dismissSplash, 3900);
        }, { once: true });
      }

      setTimeout(function () {
        if (splash.parentNode) splash.remove();
        document.body.classList.remove('splash-lock');
      }, 5100);
    }
  }

  /* ---------- Scroll-to-top button ---------- */
  const scrollTopBtn = $('#scrollTop');

  if (scrollTopBtn) {
    window.addEventListener('scroll', function () {
      const scrollY = window.scrollY || document.documentElement.scrollTop;
      const showAfter = Math.min(600, window.innerHeight * 0.6);
      scrollTopBtn.classList.toggle('visible', scrollY > showAfter);
    }, { passive: true });

    scrollTopBtn.addEventListener('click', function () {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        window.scrollTo(0, 0);
      } else {
        window.Galaxy.easeScrollTo(0, 500);
      }
    });
  }

  /* ---------- Ease-out helper for smooth scrolling ---------- */
  window.Galaxy.easeScrollTo = function (targetY, duration) {
    const startY = window.scrollY;
    const startT = performance.now();

    function step(now) {
      const progress = Math.min((now - startT) / duration, 1);
      const eased = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2;
      window.scrollTo(0, startY + (targetY - startY) * eased);
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  };

  /* ---------- Relative scroll helper (for offset anchors) ---------- */
  window.Galaxy.scrollToHash = function (hash) {
    if (!hash) return;
    const target = document.querySelector(hash);
    if (!target) return;
    const headerH = ($('#siteHeader') || { offsetHeight: 0 }).offsetHeight;
    const top = target.getBoundingClientRect().top + window.scrollY - headerH;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      window.scrollTo(0, top);
    } else {
      window.Galaxy.easeScrollTo(top > 0 ? top : 0, 700);
    }
  };

})();