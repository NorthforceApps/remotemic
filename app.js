// Keep duplicate GitHub Pages index URLs out of the user's address bar. The HTML
// canonical already points search engines at the clean directory URL.
if (window.location.pathname.endsWith('/index.html')) {
  window.history.replaceState(null, '', window.location.pathname.replace(/index\.html$/, '') + window.location.search + window.location.hash);
}

// Minimal: keep the footer year current. The site is otherwise static for speed + SEO.
document.querySelectorAll('#y').forEach(function (el) {
  el.textContent = new Date().getFullYear();
});
