/* ==========================================================================
   GALAXY RESTAURANTS — animations.js
   Hero entrance, scroll reveal, decorative touches. Reduced-motion aware.
   ========================================================================== */

(function () {
  'use strict';

  const Galaxy = window.Galaxy;
  const $$ = Galaxy.$$;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Hero entrance ---------- */
  const hero = document.querySelector('.hero');
  if (hero) {
    if (reduceMotion) {
      hero.classList.add('is-loaded');
    } else {
      const img = hero.querySelector('.hero-img');
      if (img && !img.complete) {
        img.addEventListener('load', function () { hero.classList.add('is-loaded'); }, { once: true });
      } else {
        /* Image may already be cached — trigger immediately on next frame */
        requestAnimationFrame(function () { hero.classList.add('is-loaded'); });
      }
    }
  }

  /* ---------- Scroll reveal ---------- */
  const revealEls = $$('.reveal');

  if (reduceMotion) {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  } else if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -48px 0px'
    });

    revealEls.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Gallery hover is pure CSS ---------- */
  /* ---------- Decorative ornament rotation on section head (two-cycle subtle) ---------- */
  const ornaments = $$('.ornament-inline img, .section-head .eyebrow');
  ornaments.forEach(function (orn) {
    orn.setAttribute('aria-hidden', 'true');
  });

})();