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
  const emailEl = document.getElementById('res-email');
  const locationEl = document.getElementById('res-location');
  const dateEl = document.getElementById('res-date');
  const timeEl = document.getElementById('res-time');
  const guestsEl = document.getElementById('res-guests');

  const fields = [nameEl, phoneEl, locationEl, dateEl, timeEl, guestsEl];

  /* Indian mobile number — 10 digits, first digit 6-9 (input stores it without +91) */
  const phonePattern = /^[6-9]\d{9}$/;
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /* Keep the phone field to the last 10 digits only */
  function normalizeDigits(raw) {
    const digits = (raw || '').replace(/\D/g, '');
    return digits.length > 10 ? digits.slice(-10) : digits;
  }

  phoneEl.addEventListener('input', function () {
    phoneEl.value = normalizeDigits(phoneEl.value);
    phoneEl.closest('.form-field').classList.remove('has-error');
  });

  /* Date: no typing — pick from the calendar only */
  dateEl.addEventListener('keydown', function (e) {
    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
    }
  });
  dateEl.addEventListener('paste', function (e) {
    e.preventDefault();
  });

  /* ---------- Validate a single field ---------- */
  function validateField(field) {
    const wrapper = field.closest('.form-field');
    let valid = true;
    let value = (field.value || '').trim();

    if (field === emailEl) {
      if (!value) return true; /* optional */
      valid = emailPattern.test(value);
      wrapper.classList.toggle('has-error', !valid);
      return valid;
    }

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

    if (field === phoneEl && value && !phonePattern.test(value)) {
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

  /* ---------- India clock helpers (independent of the visitor's timezone) ---------- */
  const IST_TZ = 'Asia/Kolkata';

  function istParts() {
    const out = {};
    new Intl.DateTimeFormat('en-GB', {
      timeZone: IST_TZ,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hourCycle: 'h23'
    }).formatToParts(new Date()).forEach(function (p) {
      if (p.type !== 'literal') out[p.type] = p.value;
    });
    return out;
  }

  function istTodayISO() {
    const p = istParts();
    return p.year + '-' + p.month + '-' + p.day;
  }

  function toMinutes(hhmm) {
    const parts = hhmm.split(':');
    return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
  }

  /* ---------- Set min date to today (per India time) ---------- */
  function setMinDate() {
    if (dateEl) dateEl.min = istTodayISO();
  }

  setMinDate();

  /* ---------- Time slots: on "today", hide slots already passed in India ---------- */
  function applyTimeFilter() {
    if (!dateEl.value) return true;

    const now = istParts();
    const nowMin = toMinutes(now.hour + ':' + now.minute);
    const isToday = dateEl.value === istTodayISO();

    let anyEnabled = false;
    Array.from(timeEl.options).forEach(function (opt) {
      if (!opt.value) {
        opt.disabled = true; /* the "Choose a time" placeholder stays disabled */
        return;
      }
      if (isToday && toMinutes(opt.value) <= nowMin) {
        opt.disabled = true;
        if (timeEl.value === opt.value) timeEl.value = '';
      } else {
        opt.disabled = false;
        anyEnabled = true;
      }
    });
    return anyEnabled;
  }

  dateEl.addEventListener('change', function () {
    const hasSlots = applyTimeFilter();
    if (dateEl.value && dateEl.value === istTodayISO() && !hasSlots) {
      setStatus('No time slots are left for today. Please choose another day.', 'error');
      timeEl.closest('.form-field').classList.add('has-error');
    }
  });

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

    /* 0. No time slots left for today (per India time)? */
    const hasSlots = applyTimeFilter();
    if (!hasSlots) {
      setStatus('No time slots are left for today. Please choose another day.', 'error');
      dateEl.closest('.form-field').classList.add('has-error');
      dateEl.focus();
      return;
    }

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
    const digits = normalizeDigits(phoneEl.value);
    const payload = {
      name: nameEl.value.trim(),
      phone: '+91 ' + digits,
      location: locationEl.value,
      date: dateEl.value,
      time: timeEl.value,
      guests: Number(guestsEl.value)
    };
    const emailValue = (emailEl.value || '').trim();
    if (emailValue) payload.email = emailValue;

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
      setStatus(result.message || 'Your request has been received. You will get a WhatsApp or email confirmation once the restaurant approves your booking.', 'success');
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