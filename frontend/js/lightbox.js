/* ==========================================================================
   GALAXY RESTAURANTS — lightbox.js
   Full-screen gallery lightbox with prev/next, keyboard and focus support.
   Binds to every .gallery-grid on the page.
   ========================================================================== */

(function () {
  'use strict';

  const Galaxy = window.Galaxy;
  const $$ = Galaxy.$$;

  let overlay = null;
  let items = [];
  let index = 0;
  let trigger = null;
  let lastFocused = null;

  const images = $$('.gallery-item');
  if (images.length === 0) return;

  function buildOverlay() {
    overlay = document.createElement('div');
    overlay.className = 'lightbox';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Image viewer');
    overlay.innerHTML =
      '<button class="lightbox-close" type="button" aria-label="Close">' +
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' +
          '<path d="M6 6l12 12M18 6L6 18"/>' +
        '</svg>' +
      '</button>' +
      '<figure class="lightbox-stage">' +
        '<img class="lightbox-image" src="" alt="">' +
        '<figcaption class="lightbox-caption"></figcaption>' +
      '</figure>' +
      '<button class="lightbox-prev" type="button" aria-label="Previous image">' +
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' +
          '<path d="M15 6l-6 6 6 6"/>' +
        '</svg>' +
      '</button>' +
      '<button class="lightbox-next" type="button" aria-label="Next image">' +
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">' +
          '<path d="M9 6l6 6-6 6"/>' +
        '</svg>' +
      '</button>' +
      '<span class="lightbox-count" aria-live="polite"></span>';

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay || e.target.classList.contains('lightbox-stage')) {
        close();
      }
    });
    overlay.querySelector('.lightbox-close').addEventListener('click', close);
    overlay.querySelector('.lightbox-prev').addEventListener('click', function () { show(index - 1); });
    overlay.querySelector('.lightbox-next').addEventListener('click', function () { show(index + 1); });

    document.addEventListener('keydown', function (e) {
      if (!overlay.classList.contains('is-open')) return;
      if (e.key === 'Escape') {
        close();
      } else if (e.key === 'ArrowLeft') {
        show(index - 1);
      } else if (e.key === 'ArrowRight') {
        show(index + 1);
      }
    });

    document.body.appendChild(overlay);
  }

  function collectItems(sourceItems) {
    items = sourceItems.filter(function (el) {
      return el.querySelector('img');
    }).map(function (el) {
      const img = el.querySelector('img');
      return {
        src: img.currentSrc || img.src,
        alt: img.alt,
        caption: (el.querySelector('.gallery-caption') || {}).textContent || img.alt
      };
    });
  }

  function show(newIndex) {
    if (!items.length) return;
    index = (newIndex + items.length) % items.length;
    const item = items[index];
    const image = overlay.querySelector('.lightbox-image');
    const caption = overlay.querySelector('.lightbox-caption');
    const count = overlay.querySelector('.lightbox-count');

    image.src = item.src;
    image.alt = item.alt;
    caption.textContent = item.caption;
    caption.style.visibility = item.caption ? 'visible' : 'hidden';
    count.textContent = (index + 1) + ' / ' + items.length;
    overlay.querySelector('.lightbox-prev').disabled = items.length < 2;
    overlay.querySelector('.lightbox-next').disabled = items.length < 2;
  }

  function open(clicked) {
    lastFocused = document.activeElement;
    collectItems(images);
    if (!overlay) buildOverlay();

    index = images.indexOf(clicked);
    if (index === -1) index = 0;

    overlay.classList.add('is-open');
    document.body.classList.add('lightbox-open');
    show(index);
    overlay.querySelector('.lightbox-close').focus();
  }

  function close() {
    if (!overlay) return;
    overlay.classList.remove('is-open');
    document.body.classList.remove('lightbox-open');
    if (lastFocused) lastFocused.focus();
  }

  images.forEach(function (image, i) {
    image.addEventListener('click', function () {
      open(image);
    });
    image.setAttribute('tabindex', '0');
    image.setAttribute('role', 'button');
    image.setAttribute('aria-label', (image.querySelector('.gallery-caption') || {}).textContent || 'Open image in viewer');
    image.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open(image);
      }
    });
  });

})();