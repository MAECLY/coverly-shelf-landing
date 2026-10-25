/* The two interactive bits of the page, both optional (the page reads the
   same without them):
   1. A CSS box turns when dragged, or with the arrow keys once focused
      (the hero's box, or the one in "what it adds").
   2. The screenshot thumbnails open a lightbox that works like the extension's:
      Left/Right to move, Escape to close. */
(function () {
  "use strict";

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function turnable(box) {
    var ry = 32, rx = -8, start = null;
    function set() {
      box.style.setProperty("--ry", ry + "deg");
      box.style.setProperty("--rx", rx + "deg");
    }
    function touch() { box.classList.add("touched"); }
    box.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      start = { x: e.clientX, y: e.clientY, ry: ry, rx: rx };
      box.setPointerCapture(e.pointerId);
      box.classList.add("dragging");
      touch();
    });
    box.addEventListener("pointermove", function (e) {
      if (!start) return;
      ry = start.ry + (e.clientX - start.x) * 0.6;
      rx = clamp(start.rx - (e.clientY - start.y) * 0.3, -30, 20);
      set();
    });
    function end() { start = null; box.classList.remove("dragging"); }
    box.addEventListener("pointerup", end);
    box.addEventListener("pointercancel", end);
    box.addEventListener("keydown", function (e) {
      var step = { ArrowLeft: [-20, 0], ArrowRight: [20, 0], ArrowUp: [0, 8], ArrowDown: [0, -8] }[e.key];
      if (e.key === "Home") { ry = 32; rx = -8; }
      else if (step) { ry += step[0]; rx = clamp(rx + step[1], -30, 20); }
      else return;
      e.preventDefault();
      touch();
      set();
    });
  }

  function lightbox(dialog, thumbs) {
    var shot = dialog.querySelector(".lightbox-shot");
    var caption = dialog.querySelector("[data-caption]");
    var count = dialog.querySelector("[data-count]");
    var at = 0, opener = null;
    function show(i) {
      at = (i + thumbs.length) % thumbs.length;
      var t = thumbs[at];
      var light = document.documentElement.getAttribute("data-theme") === "light";
      shot.src = (light && t.getAttribute("data-full-light")) || t.getAttribute("data-full");
      shot.alt = t.getAttribute("aria-label");
      caption.textContent = t.getAttribute("aria-label");
      count.textContent = (at + 1) + " / " + thumbs.length;
    }
    thumbs.forEach(function (t, i) {
      t.addEventListener("click", function () {
        opener = t;
        show(i);
        dialog.showModal();
      });
    });
    dialog.querySelector("[data-prev]").addEventListener("click", function () { show(at - 1); });
    dialog.querySelector("[data-next]").addEventListener("click", function () { show(at + 1); });
    dialog.querySelector("[data-close]").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); show(at - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); show(at + 1); }
    });
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", function () { if (opener) opener.focus(); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var box = document.querySelector(".hero .box, .pic-box .box");
    if (box) turnable(box);
    var dialog = document.querySelector(".lightbox");
    var thumbs = Array.prototype.slice.call(document.querySelectorAll(".strip [data-full]"));
    if (dialog && dialog.showModal && thumbs.length) lightbox(dialog, thumbs);
    else thumbs.forEach(function (t) { t.disabled = true; });
  });
})();
