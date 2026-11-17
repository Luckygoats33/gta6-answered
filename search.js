/* Site search for callunc.com. Reads search.json (built by build.py) and filters it in the browser. */
(function () {
  var input = document.getElementById('q'), list = document.getElementById('results'),
      status = document.getElementById('search-status'), tries = document.getElementById('search-try');
  if (!input || !list) return;
  var index = null, STOP = { the: 1, a: 1, an: 1, is: 1, of: 1, on: 1, in: 1, to: 1, for: 1, and: 1, do: 1, does: 1, i: 1, it: 1, what: 1, when: 1, how: 1, can: 1, you: 1, will: 1, be: 1, my: 1, gta: 1, '6': 1, vi: 1 };

  function norm(s) { return (s || '').toLowerCase().replace(/[‘’']/g, '').replace(/[^a-z0-9$.]+/g, ' ').trim(); }
  function stem(w) { return w.length > 3 ? w.replace(/(ing|es|s)$/, '') : w; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function prep(items) {
    items.forEach(function (o) { o._t = ' ' + norm(o.t) + ' '; o._d = ' ' + norm(o.d) + ' '; o._x = ' ' + norm(o.x) + ' '; o._s = ' ' + norm(o.s) + ' '; });
    return items;
  }

  function search(q) {
    var words = norm(q).split(' ').filter(Boolean);
    var terms = words.filter(function (w) { return !STOP[w]; });
    if (!terms.length) terms = words;          // a query that is only "gta 6" still searches
    terms = terms.map(stem);
    var phrase = ' ' + norm(q);
    var out = [];
    index.forEach(function (o) {
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = ' ' + terms[i], s = 0;
        if (o._t.indexOf(t) > -1) s += 10;
        if (o._s.indexOf(t) > -1) s += 8;
        if (o._d.indexOf(t) > -1) s += 4;
        if (o._x.indexOf(t) > -1) s += 1;
        if (!s) return;                        // every word has to match somewhere
        score += s;
      }
      if (o._t.indexOf(phrase) > -1) score += 15;
      score += o.w || 0;
      out.push([score, o]);
    });
    out.sort(function (a, b) { return b[0] - a[0]; });
    return out.slice(0, 40).map(function (r) { return r[1]; });
  }

  function render() {
    var q = input.value.trim();
    if (tries) tries.hidden = !!q;
    if (!q) { list.innerHTML = ''; status.textContent = ''; return; }
    if (!index) { status.textContent = 'Loading…'; return; }
    var hits = search(q);
    status.textContent = hits.length ? hits.length + (hits.length === 1 ? ' result' : ' results') + ' for “' + q + '”'
      : 'Nothing found for “' + q + '”. Try fewer words, like “pre-load” or “price”.';
    list.innerHTML = hits.map(function (o) {
      var ext = /^https?:/.test(o.u);
      return '<li class="post-card"><a href="' + esc(ext ? o.u : '../' + o.u) + '"' + (ext ? ' target="_blank" rel="noopener nofollow"' : '') + '>' +
        '<span class="post-date">' + esc(o.k) + '</span><span class="post-title">' + esc(o.t) + '</span>' +
        (o.d ? '<span class="post-desc">' + esc(o.d) + '</span>' : '') + '</a></li>';
    }).join('');
  }

  var timer, gaTimer, lastSent = '';
  function track() {            // tells Google Analytics what people search for (only once GA is switched on)
    var q = input.value.trim().toLowerCase();
    if (!q || q === lastSent || typeof window.gtag !== 'function' || !index) return;
    lastSent = q;
    window.gtag('event', 'search', { search_term: q, results: list.children.length });
  }
  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      render();
      var q = input.value.trim();
      clearTimeout(gaTimer); gaTimer = setTimeout(track, 1500);
      try { history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) : location.pathname); } catch (e) {}
    }, 120);
  });
  document.getElementById('search-form').addEventListener('submit', function (e) { e.preventDefault(); render(); input.blur(); });

  var start = new URLSearchParams(location.search).get('q');
  if (start) input.value = start; else input.focus();
  render();
  fetch('../search.json').then(function (r) { return r.json(); }).then(function (d) { index = prep(d); render(); track(); })
    .catch(function () { status.textContent = 'Search could not load. Refresh the page to try again.'; });
})();
