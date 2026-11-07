(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#navigation');
  if (menu && nav) {
    menu.hidden = false;
    const closeMenu = () => { nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); };
    menu.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', (event) => { if (event.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('open')) { closeMenu(); menu.focus(); }
    });
    document.addEventListener('click', (event) => { if (!event.target.closest('.site-header')) closeMenu(); });
  }
  const scene = document.querySelector('#laptop-scene');
  const laptop = document.querySelector('#laptop');
  const toggle = document.querySelector('#motion-toggle');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false;
  try { paused = localStorage.getItem('faris-motion-paused') === 'true'; } catch (_) { /* Optional preference storage. */ }
  const resetTilt = () => { if (laptop) { laptop.style.removeProperty('--tilt-x'); laptop.style.removeProperty('--tilt-y'); } };
  const updateMotion = () => {
    document.body.classList.toggle('motion-paused', paused || reduceMotion.matches);
    if (toggle) {
      toggle.hidden = reduceMotion.matches;
      toggle.textContent = paused ? 'Resume motion' : 'Pause motion';
      toggle.setAttribute('aria-pressed', String(paused));
    }
    resetTilt();
  };
  updateMotion();
  reduceMotion.addEventListener('change', updateMotion);
  if (toggle) toggle.addEventListener('click', () => {
    paused = !paused; updateMotion();
    try { localStorage.setItem('faris-motion-paused', String(paused)); } catch (_) { /* Ignore blocked storage. */ }
  });
  if (scene && laptop) {
    let frame = 0;
    scene.addEventListener('pointermove', (event) => {
      if (paused || reduceMotion.matches || event.pointerType !== 'mouse') return;
      const bounds = scene.getBoundingClientRect();
      const x = (event.clientX - bounds.left) / bounds.width - 0.5;
      const y = (event.clientY - bounds.top) / bounds.height - 0.5;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        laptop.style.setProperty('--tilt-y', (-17 + x * 16) + 'deg');
        laptop.style.setProperty('--tilt-x', (6 - y * 10) + 'deg');
      });
    });
    scene.addEventListener('pointerleave', () => { cancelAnimationFrame(frame); resetTilt(); });
  }
  const filters = document.querySelector('.filters');
  const cards = Array.from(document.querySelectorAll('.project-card'));
  if (filters && cards.length) {
    filters.hidden = false;
    filters.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-filter]');
      if (!button) return;
      const category = button.dataset.filter;
      filters.querySelectorAll('button').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      let visible = 0;
      cards.forEach((card) => {
        card.hidden = category !== 'all' && card.dataset.category !== category;
        if (!card.hidden) visible += 1;
      });
      document.querySelector('#filter-status').textContent = visible + ' project' + (visible === 1 ? '' : 's') + ' shown.';
      document.querySelector('#no-projects').hidden = visible !== 0;
    });
  }
})();
