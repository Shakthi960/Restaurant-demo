/* ==========================================================================
   GALAXY RESTAURANTS — reservation.js
   Frontend validation + POST to FastAPI /api/reservations
   ========================================================================== */

(function () {
  'use strict';

  const Galaxy = window.Galaxy;
  const form = document.getElementById('reservationForm');
  if (!form) return;

  const statusEl = document.getElementById('formStatus');
  const submitBtn = form.querySelector('.btn[type="submit"]');

  const nameEl = document.getElementById('res-name');
  const phoneEl = document.getElementById('res-phone');
  const locationEl = document.getElementById('res-location');
  const dateEl = document.getElementById('res-date');
  const timeEl = document.getElementById('res-time');
  const guestsEl = document.getElementById('res-guests');

  const fields = [nameEl, phoneEl, locationEl, dateEl, timeEl, guestsEl];

  /* Indian mobile number — +91 / 0 prefix optional */
  const phonePattern = /^(\+91[\s-]?|0)?[6-9]\d{9}$/;

  /* ---------- Validate a single field ---------- */
  function validateField(field) {
    const wrapper = field.closest('.form-field');
    let valid = true;
    const value = (field.value || '').trim();

    if (!value) {
      valid = false;
    }

    if (field === dateEl && value) {
      /* Date must not be in the past */
      const selected = new Date(value + 'T00:00:00');
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (selected < today) valid = false;
    }

    if (field === phoneEl && value && !phonePattern.test(value.replace(/\s+/g, ''))) {
      valid = false;
    }

    wrapper.classList.toggle('has-error', !valid);
    return valid;
  }

  /* ---------- Live clear of error states ---------- */
  fields.forEach(function (field) {
    field.addEventListener('change', function () {
      const wrapper = field.closest('.form-field');
      if (field.value) {
        wrapper.classList.remove('has-error');
        if (field === dateEl && statusEl.classList.contains('is-error')) {
          setStatus('');
        }
      }
    });
  });

  fields.forEach(function (field) {
    field.addEventListener('input', function () {
      const wrapper = field.closest('.form-field');
      if (field.value) wrapper.classList.remove('has-error');
    });
  });

  /* ---------- Set min date to today ---------- */
  function setMinDate() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    if (dateEl) dateEl.min = yyyy + '-' + mm + '-' + dd;
  }

  setMinDate();

  /* ---------- Status helpers ---------- */
  function setStatus(message, type) {
    statusEl.textContent = message;
    statusEl.classList.remove('is-error', 'is-success');
    if (type) statusEl.classList.add(type === 'error' ? 'is-error' : 'is-success');
  }

  function clearStatus() {
    const wrapper = form.closest('.reservation-form');
    wrapper.classList.remove('is-submitting');
    statusEl.textContent = '';
    statusEl.classList.remove('is-error', 'is-success');
  }

  /* ---------- Submit handler ---------- */
  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    /* 1. Validate all fields */
    let formValid = true;
    fields.forEach(function (field) {
      if (!validateField(field)) formValid = false;
    });

    if (!formValid) {
      setStatus('Please complete all fields to reserve your table.', 'error');
      /* Focus the first invalid field for accessibility */
      const firstInvalid = fields.find(function (f) { return !f.value; }) || dateEl;
      firstInvalid.focus();
      return;
    }

    /* 2. Build payload for POST /api/reservations */
    const payload = {
      name: nameEl.value.trim(),
      phone: phoneEl.value.trim(),
      location: locationEl.value,
      date: dateEl.value,
      time: timeEl.value,
      guests: Number(guestsEl.value)
    };

    /* 3. Submit to the FastAPI backend */
    form.classList.add('is-submitting');
    submitBtn.setAttribute('aria-busy', 'true');
    setStatus('Reserving your table…');

    try {
      const response = await fetch('/api/reservations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || 'Something went wrong. Please try again.');
      }
      setStatus(result.message || 'Thank you! Your table request has been received.', 'success');
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