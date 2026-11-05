// Scene flow: the page background takes the palette of the scene in the middle of the
// screen, content animates in once, and videos play only while visible.
(function () {
  var root = document.documentElement;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var scenes = document.querySelectorAll('.scene');
  var rail = document.querySelector('.rail');
  var railLinks = rail ? rail.querySelectorAll('a') : [];

  if (!('IntersectionObserver' in window)) return;
  root.classList.add('js');

  scenes.forEach(function (s) {
    s.querySelectorAll('.fx').forEach(function (el, i) { el.style.setProperty('--i', i); });
  });

  // Reveal each scene once when a fifth of it is on screen.
  var revealer = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      revealer.unobserve(e.target);
    });
  }, { threshold: 0.2 });

  // The scene crossing the middle line sets the theme and the rail position.
  var theme = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var s = e.target;
      document.body.dataset.scene = s.dataset.scene;
      if (!rail) return;
      var hit = false;
      railLinks.forEach(function (a) {
        var cur = a.dataset.for === s.id;
        a.classList.toggle('cur', cur);
        if (cur) { a.setAttribute('aria-current', 'true'); hit = true; } else { a.removeAttribute('aria-current'); }
      });
      rail.classList.toggle('on', hit);
    });
  }, { rootMargin: '-50% 0px -50% 0px' });

  scenes.forEach(function (s) { revealer.observe(s); theme.observe(s); });

  // Videos: autoplay in view (unless reduced motion), with a play/pause button each.
  document.querySelectorAll('.screen').forEach(function (box) {
    var v = box.querySelector('video');
    var btn = box.querySelector('.vbtn');
    if (!v || !btn) return; // image-only screens (e.g. animated SVG) have no controls
    var userPaused = reduced;
    function sync() {
      var playing = !v.paused;
      btn.setAttribute('aria-pressed', String(playing));
      btn.setAttribute('aria-label', playing ? 'Pause video' : 'Play video');
    }
    function play() {
      var p = v.play();
      if (p && p.catch) p.catch(function () { sync(); });
    }
    v.addEventListener('play', sync);
    v.addEventListener('pause', sync);
    btn.addEventListener('click', function () {
      if (v.paused) { userPaused = false; play(); } else { userPaused = true; v.pause(); }
    });
    new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !userPaused) play();
        else if (!e.isIntersecting && !v.paused) v.pause();
      });
    }, { threshold: 0.35 }).observe(v);
  });
})();
