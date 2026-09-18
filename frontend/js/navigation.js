/* ==========================================================================
   GALAXY RESTAURANTS — navigation.js
   Sticky header, mobile drawer, active nav state, smooth anchor scrolling.
   ========================================================================== */

(function () {
  'use strict';

  const Galaxy = window.Galaxy;
  const $ = Galaxy.$;
  const $$ = Galaxy.$$;

  const header = $('#siteHeader');
  const hamburger = $('#hamburger');
  const mainNav = $('#mainNav');
  const brand = $('.brand');
  const sections = $$('main section[id], .site-footer');

  /* ---------- Sticky header state ---------- */
  let lastScroll = 0;

  function updateHeader() {
    const scrollY = window.scrollY || document.documentElement.scrollTop;
    header.classList.toggle('scrolled', scrollY > 30);
    lastScroll = scrollY;
  }

  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();

  /* ---------- Mobile navigation drawer ---------- */
  function isMobileNav() {
    return window.getComputedStyle(hamburger).display !== 'none';
  }

  function openNav() {
    mainNav.classList.add('is-open');
    hamburger.classList.add('is-open');
    hamburger.setAttribute('aria-expanded', 'true');
    hamburger.setAttribute('aria-label', 'Close menu');
    document.body.style.overflow = 'hidden';
  }

  function closeNav() {
    mainNav.classList.remove('is-open');
    hamburger.classList.remove('is-open');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.setAttribute('aria-label', 'Open menu');
    document.body.style.overflow = '';
  }

  hamburger.addEventListener('click', function () {
    mainNav.classList.contains('is-open') ? closeNav() : openNav();
  });

  /* Close drawer when a nav link is clicked */
  mainNav.addEventListener('click', function (e) {
    if (e.target.closest('a')) {
      setTimeout(closeNav, 80);
    }
  });

  /* Close drawer on Escape */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mainNav.classList.contains('is-open')) closeNav();
  });

  /* Prevent body scroll when drawer is open on resize to desktop */
  window.addEventListener('resize', function () {
    if (!isMobileNav()) closeNav();
  });

  /* ---------- Active navigation link highlighting ---------- */
  const navLinks = $$('.nav-link');
  let activeLink = navLinks[0] || null;

  function setActive(link) {
    if (activeLink) activeLink.classList.remove('active');
    activeLink = link;
    activeLink.classList.add('active');
  }

  /* Fade brand on scroll for subtle compact feel */
  function handleScrollSpy() {
    const scrollPos = window.scrollY;
    const offset = 120;

    for (let i = sections.length - 1; i >= 0; i--) {
      const section = sections[i];
      const top = section.offsetTop - offset;
      const bottom = top + section.offsetHeight;

      if (scrollPos >= top && scrollPos < bottom) {
        const id = section.getAttribute('id');
        const link = navLinks.find(function (l) { return l.getAttribute('href') === '#' + id; });
        if (link) setActive(link);
        break;
      }
    }
  }

  window.addEventListener('scroll', handleScrollSpy, { passive: true });

  /* ---------- Smooth scrolling with header offset ---------- */
  const allAnchorLinks = $$('a[href^="#"]');

  allAnchorLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      const href = link.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      Galaxy.scrollToHash(href);
    });
  });

})();