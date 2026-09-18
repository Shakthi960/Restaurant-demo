/* ==========================================================================
   GALAXY RESTAURANTS — contact.js
   Frontend validation + POST to FastAPI /api/contact
   ========================================================================== */

(function () {
  'use strict';

  const Galaxy = window.Galaxy;
  const form = document.getElementById('contactForm');
  if (!form) return;

  const statusEl = document.getElementById('contactStatus');
  const submitBtn = form.querySelector('.btn[type="submit"]');

  const nameEl = document.getElementById('contact-name');
  const emailEl = document.getElementById('contact-email');
  const phoneEl = document.getElementById('contact-phone');
  const messageEl = document.getElementById('contact-message');

  const fields = [nameEl, emailEl, phoneEl, messageEl];

  /* Simple email sanity check */
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  /* ---------- Validate a single field ---------- */
  function validateField(field) {
    const wrapper = field.closest('.form-field');
    const value = (field.value || '').trim();

    if (value && field === emailEl && !emailPattern.test(value)) {
      wrapper.classList.add('has-error');
      return false;
    }

    if (field !== phoneEl && !value) {
      wrapper.classList.add('has-error');
      return false;
    }

    wrapper.classList.remove('has-error');
    return true;
  }

  /* ---------- Live clear of error states ---------- */
  fields.forEach(function (field) {
    ['input', 'change'].forEach(function (eventType) {
      field.addEventListener(eventType, function () {
        const wrapper = field.closest('.form-field');
        wrapper.classList.remove('has-error');
      });
    });
  });

  /* ---------- Status helpers ---------- */
  function setStatus(message, type) {
    statusEl.textContent = message;
    statusEl.classList.remove('is-error', 'is-success');
    if (type) statusEl.classList.add(type === 'error' ? 'is-error' : 'is-success');
  }

  function clearStatus() {
    statusEl.textContent = '';
    statusEl.classList.remove('is-error', 'is-success');
  }

  /* ---------- Submit handler ---------- */
  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    let formValid = true;
    fields.forEach(function (field) {
      if (!validateField(field)) formValid = false;
    });

    if (!formValid) {
      setStatus('Please complete the highlighted fields.', 'error');
      const firstInvalid = fields.find(function (f) {
        return f.closest('.form-field').classList.contains('has-error');
      });
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    const payload = {
      name: nameEl.value.trim(),
      email: emailEl.value.trim(),
      phone: (phoneEl.value || '').trim(),
      message: messageEl.value.trim()
    };

    form.classList.add('is-submitting');
    submitBtn.setAttribute('aria-busy', 'true');
    setStatus('Sending your message…');

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || 'Something went wrong. Please try again.');
      }
      setStatus(result.message || 'Thank you for writing to us. We will be in touch shortly.', 'success');
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