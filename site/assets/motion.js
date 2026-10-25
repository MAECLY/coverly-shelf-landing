/* What moves, once, and only towards the finished page the HTML already
   shows. theme.js sets html.anim in <head> (no reduced motion, no
   Save-Data); this file adds html.motion once its setup worked, and
   .is-in to each block as it scrolls in (motion.css plays the rest). Any
   error, or reduced motion turned on mid-visit, runs halt(): every block
   is put in its finished state and both classes go. */
(function () {
  "use strict";

  var html = document.documentElement;
  var stops = [];
  /* [selector, share of the block on screen before it plays] */
  var REVEAL = [
    [".section h2, .section .intro, .notes, .aside-card, .credits-grid > *, .faq, .lists-grid .stage, .rowmock, .promises, .steps", 0.3],
    [".shot-card", 0.35],
    [".feature, .seg, .manifest", 0.5]
  ];

  function halt() {
    var list = stops;
    stops = [];
    for (var i = 0; i < list.length; i++) {
      try { list[i](); } catch (e) {}
    }
    html.classList.remove("anim", "motion");
  }

  function onScreen(el) {
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.bottom > 0 && r.top < innerHeight;
  }

  function settle(el) {
    el.classList.add("is-in", "no-anim");
  }

  function reveal(el, t) {
    if (onScreen(el)) return settle(el);
    /* A block taller than the screen could never reach its share. */
    if (el.getBoundingClientRect().height * t > innerHeight * 0.8) t = 0.1;
    var io = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          io.disconnect();
          el.classList.add("is-in");
          return;
        }
      }
    }, { threshold: t });
    io.observe(el);
    stops.push(function () { io.disconnect(); settle(el); });
  }

  function start() {
    if (!html.classList.contains("anim") || !window.IntersectionObserver || !window.matchMedia) {
      html.classList.remove("anim");
      return;
    }
    try {
      /* A late load skips the hero straight to its end frame. */
      if (performance.now() > 2500) {
        var late = document.querySelectorAll(".hero, .topbar");
        for (var k = 0; k < late.length; k++) late[k].classList.add("no-anim");
      }
      for (var g = 0; g < REVEAL.length; g++) {
        var els = document.querySelectorAll(REVEAL[g][0]);
        for (var i = 0; i < els.length; i++) reveal(els[i], REVEAL[g][1]);
      }
      html.classList.add("motion");
    } catch (e) {
      halt();
      return;
    }
    var still = matchMedia("(prefers-reduced-motion: reduce)");
    var calm = function () { if (still.matches) halt(); };
    if (still.addEventListener) still.addEventListener("change", calm);
    else if (still.addListener) still.addListener(calm);
    window.addEventListener("error", halt);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
