/* ==========================================================================
   GALAXY RESTAURANTS — review.js
   Star-rating review form + POST to FastAPI /api/reviews
   New reviews are stored unapproved (hidden) until moderation.
   ========================================================================== */

(function () {
  'use strict';

  const form = document.getElementById('reviewForm');
  if (!form) return;

  const statusEl = document.getElementById('reviewStatus');
  const submitBtn = form.querySelector('.btn[type="submit"]');

  const nameEl = document.getElementById('review-name');
  const cityEl = document.getElementById('review-city');
  const ratingInputs = Array.prototype.slice.call(form.querySelectorAll('input[name="rating"]'));
  const textEl = document.getElementById('review-text');

  function selectedRating() {
    const chosen = ratingInputs.filter(function (input) { return input.checked; });
    return chosen.length ? Number(chosen[0].value) : 0;
  }

  function setRatingError(valid) {
    const wrapper = form.querySelector('.star-rating').closest('.form-field');
    wrapper.classList.toggle('has-error', !valid);
  }

  function validateField(field) {
    const wrapper = field.closest('.form-field');
    const value = (field.value || '').trim();
    const valid = field === cityEl || value.length > 0;
    wrapper.classList.toggle('has-error', !valid);
    return valid;
  }

  function setStatus(message, type) {
    statusEl.textContent = message;
    statusEl.classList.remove('is-error', 'is-success');
    if (type) statusEl.classList.add(type === 'error' ? 'is-error' : 'is-success');
  }

  function clearStatus() {
    statusEl.textContent = '';
    statusEl.classList.remove('is-error', 'is-success');
  }

  form.querySelectorAll('input, textarea').forEach(function (el) {
    ['input', 'change'].forEach(function (eventType) {
      el.addEventListener(eventType, function () {
        if (el.name === 'rating') {
          setRatingError(true);
        } else {
          el.closest('.form-field').classList.remove('has-error');
        }
        if (statusEl.classList.contains('is-error')) setStatus('');
      });
    });
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    let formValid = true;
    formValid = validateField(nameEl) && formValid;
    formValid = validateField(textEl) && formValid;

    const rating = selectedRating();
    setRatingError(rating > 0);
    if (rating === 0) formValid = false;

    if (!formValid) {
      setStatus('Please add your name, a rating and a few words.', 'error');
      return;
    }

    const payload = {
      author: nameEl.value.trim(),
      city: (cityEl.value || '').trim(),
      rating: rating,
      review: textEl.value.trim()
    };

    form.classList.add('is-submitting');
    submitBtn.setAttribute('aria-busy', 'true');
    setStatus('Submitting your review…');

    try {
      const response = await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || 'Something went wrong. Please try again.');
      }
      setStatus(result.message || 'Thank you! Your review will appear after moderation.', 'success');
      form.reset();
    } catch (err) {
      setStatus(err.message || 'Could not reach the server. Please try again later.', 'error');
    } finally {
      form.classList.remove('is-submitting');
      submitBtn.removeAttribute('aria-busy');
    }

    setTimeout(clearStatus, 6000);
  });

})();