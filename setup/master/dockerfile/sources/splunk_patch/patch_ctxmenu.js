// ---------------------------------------------------------------------------
// OSIR right-click context menu (shared with the Timeline-Explorer dashboards):
// search the highlighted text in the raw logs, pivot on host / time, flag events.
// The script itself lives in the Timeline-Explorer app (appserver/static).
// ---------------------------------------------------------------------------
(function () {
    if (window.__osirCtxMenu || document.querySelector('script[src*="osir_context_menu.js"]')) { return; }
    var locale = (window.$C && window.$C.LOCALE) || location.pathname.split('/')[1] || 'en-US';
    var root = ((window.$C && window.$C.MRSPARKLE_ROOT_PATH) || '').replace(/\/$/, '');
    var s = document.createElement('script');
    // cache-busting: Splunk serves app static files with a one-year max-age
    s.src = root + '/' + locale + '/static/app/Timeline-Explorer/osir_context_menu.js?v=' + Date.now();
    (document.head || document.documentElement).appendChild(s);
})();
