/* Preserve the left sidebar scroll position across page navigations.
 * The sidebar is re-rendered on every page, so its scroll offset is stored
 * in sessionStorage on scroll and restored when the new page loads. The
 * restore is re-applied after Alpine.js has expanded the current section,
 * because the sidebar height changes at that point. */
(function () {
  /* The scrollable element is the sidebar aside itself (overflow-y-auto). */
  var sidebar = document.getElementById("left-sidebar");
  if (!sidebar) {
    return;
  }
  var key = "osir-sidebar-scroll";
  var timer = null;

  sidebar.addEventListener("scroll", function () {
    if (timer !== null) {
      clearTimeout(timer);
    }
    timer = setTimeout(function () {
      try {
        sessionStorage.setItem(key, String(sidebar.scrollTop));
      } catch (e) {
        /* sessionStorage unavailable: ignore */
      }
    }, 100);
  });

  function restore() {
    var saved = null;
    try {
      saved = sessionStorage.getItem(key);
    } catch (e) {
      return;
    }
    if (saved !== null) {
      var offset = parseInt(saved, 10);
      if (!isNaN(offset)) {
        sidebar.scrollTop = offset;
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", restore);
  } else {
    restore();
  }
  /* Re-apply once Alpine.js has expanded the current navigation branch. */
  document.addEventListener("alpine:initialized", restore);
  setTimeout(restore, 250);
})();
