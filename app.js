(function () {
  var SOURCE = 'remotemic_site';
  var PACKAGE = 'com.stream.remotemic';
  var HOME_DIRS = ['ja', 'de', 'fr', 'es', 'hi', 'remotemic', 'ar', 'pt-br'];
  function campaign() {
    var parts = window.location.pathname.split("/").filter(Boolean);
    var page = parts[parts.length - 1] || "";
    var inGuides = parts.indexOf("guides") !== -1 || page === "guides.html";
    if (!page || HOME_DIRS.indexOf(page) !== -1 || page === "index.html") {
      return inGuides ? "guide_hub" : "site_home";
    }
    var slug = page.replace(/\.html$/, "");
    if (slug === "privacy") return "site_privacy";
    if (slug === "data-deletion") return "site_data_deletion";
    if (inGuides || page === "guides.html") {
      if (slug === "guides") return "guide_hub";
      return "guide_" + slug.replace(/-/g, "_");
    }
    return "site_" + slug.replace(/-/g, "_");
  }
  function localeFromPath() {
    var parts = window.location.pathname.split("/").filter(Boolean);
    var locales = { de: 1, fr: 1, es: 1, hi: 1, ja: 1, ar: 1, "pt-br": 1, ko: 1, pt: 1, zh: 1 };
    for (var i = 0; i < parts.length; i++) {
      if (locales[parts[i]]) return parts[i];
    }
    return "en";
  }
  var url = new URL("https://play.google.com/store/apps/details?id=" + PACKAGE);
  url.searchParams.set(
    "referrer",
    "utm_source=" + SOURCE + "&utm_medium=organic&utm_campaign=" + campaign() + "&utm_content=" + localeFromPath()
  );
  document.querySelectorAll('a[href*="play.google.com/store/apps/details"]').forEach(function (a) {
    a.href = url.toString();
  });
})();

// Keep duplicate GitHub Pages index URLs out of the user's address bar. The HTML
// canonical already points search engines at the clean directory URL.
if (window.location.pathname.endsWith('/index.html')) {
  window.history.replaceState(null, '', window.location.pathname.replace(/index\.html$/, '') + window.location.search + window.location.hash);
}

// Minimal: keep the footer year current. The site is otherwise static for speed + SEO.
document.querySelectorAll('#y').forEach(function (el) {
  el.textContent = new Date().getFullYear();
});

