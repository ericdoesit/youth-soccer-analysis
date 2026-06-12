/* Shared site navigation. Include where the nav should render:
   root pages:    <script src="nav.js"></script>
   report pages:  <script src="../nav.js"></script>
   Edit the PAGES list here once; every page updates. */
(function () {
  var script = document.currentScript;
  var prefix = script.getAttribute('src').indexOf('../') === 0 ? '../' : '';

  var PAGES = [
    ['index.html',              'Home',    ''],
    ['report/scope.html',       'Scope',   ''],
    ['report/costs.html',       'Costs',   ''],
    ['report/fools_gold.html',  'ROI',     ''],
    ['report/mls.html',         'MLS',     ''],
    ['report/equity.html',      'Equity',  ''],
    ['report/methodology.html', 'Methods', 'nav-appendix'],
    ['report/data.html',        'Data',    'nav-appendix'],
    ['survey.html',             'Survey',  'nav-survey'],
  ];

  var path = location.pathname;
  function isActive(file) {
    var name = file.split('/').pop();
    if (name === 'index.html') {
      return /(^|\/)(index\.html)?$/.test(path) && path.indexOf('/report/') === -1;
    }
    return path.indexOf(name) !== -1;
  }

  var links = PAGES.map(function (p) {
    var cls = [p[2], isActive(p[0]) ? 'active' : ''].filter(Boolean).join(' ');
    return '<a href="' + prefix + p[0] + '"' + (cls ? ' class="' + cls + '"' : '') + '>' + p[1] + '</a>';
  }).join('\n      ');

  var html =
    '<nav class="site-nav">\n' +
    '  <div class="nav-inner">\n' +
    '    <a href="' + prefix + 'index.html" class="nav-brand">Pitfalls on the <span>Pathway</span></a>\n' +
    '    <button class="nav-toggle" aria-label="Toggle menu" onclick="this.nextElementSibling.classList.toggle(\'open\')">\n' +
    '      <span></span><span></span><span></span>\n' +
    '    </button>\n' +
    '    <div class="nav-links">\n      ' + links + '\n    </div>\n' +
    '  </div>\n' +
    '</nav>';

  script.insertAdjacentHTML('afterend', html);
})();
