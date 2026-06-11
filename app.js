// Minimal: keep the footer year current. The site is otherwise static for speed + SEO.
document.querySelectorAll('#y').forEach(function (el) {
  el.textContent = new Date().getFullYear();
});
