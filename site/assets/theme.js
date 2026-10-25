/* Runs in <head>, before first paint: colour mode and the motion gate.
   No-JS visitors get the system mode through CSS alone. Same contract as
   the Coverly ROMs landing (the "coverly:mode" key is shared by design:
   both sites live under maecly.com but on different origins, so each keeps
   its own copy). */
(function () {
  "use strict";
  var html = document.documentElement;
  var KEY = "coverly:mode";
  var BG = { light: "#f2f3ef", dark: "#121514" }; /* --cr-bg (design/tokens.json) */
  var dark = window.matchMedia ? matchMedia("(prefers-color-scheme: dark)") : null;

  html.classList.add("js");

  function read() {
    try {
      var m = localStorage.getItem(KEY);
      return m === "light" || m === "dark" ? m : "system";
    } catch (e) {
      return "system";
    }
  }
  function resolve(mode) {
    return mode === "system" ? (dark && dark.matches ? "dark" : "light") : mode;
  }
  function apply(mode) {
    var theme = resolve(mode);
    html.setAttribute("data-theme", theme);
    html.setAttribute("data-mode", mode);
    var metas = document.querySelectorAll('meta[name="theme-color"]');
    for (var i = 0; i < metas.length; i++) {
      metas[i].content = mode === "system" ? (metas[i].media.indexOf("dark") > -1 ? BG.dark : BG.light) : BG[theme];
    }
    var radios = document.querySelectorAll('input[name="mode"]');
    for (var j = 0; j < radios.length; j++) radios[j].checked = radios[j].value === mode;
  }

  var mode = read();
  apply(mode);

  /* Motion only when nobody asked for less of it. */
  var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var save = navigator.connection && navigator.connection.saveData;
  if (!still && !save) html.classList.add("anim");

  function follow() { if (mode === "system") apply(mode); }
  if (dark) {
    if (dark.addEventListener) dark.addEventListener("change", follow);
    else if (dark.addListener) dark.addListener(follow);
  }

  document.addEventListener("DOMContentLoaded", function () {
    apply(mode);
    var radios = document.querySelectorAll('input[name="mode"]');
    for (var i = 0; i < radios.length; i++) {
      radios[i].addEventListener("change", function (e) {
        mode = e.target.value;
        try {
          if (mode === "system") localStorage.removeItem(KEY);
          else localStorage.setItem(KEY, mode);
        } catch (err) {}
        apply(mode);
      });
    }
  });
})();
