/* Playground site script. Vanilla JS, no dependencies. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(pointer: fine)').matches;
  var cfg = window.PG || {};

  /* Mobile menu */
  var menuBtn = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.nav-links');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        nav.classList.remove('open');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.focus();
      }
    });
  }

  /* Header shrink / hide on scroll, scroll progress bar */
  var header = document.querySelector('.site-header');
  var progress = document.querySelector('.scroll-progress');
  var lastY = window.scrollY;
  var ticking = false;
  function onScroll() {
    var y = window.scrollY;
    if (header) {
      header.classList.toggle('is-scrolled', y > 20);
      var menuOpen = nav && nav.classList.contains('open');
      header.classList.toggle('is-hidden', !menuOpen && y > 400 && y > lastY + 4);
      if (y < lastY - 4) header.classList.remove('is-hidden');
    }
    if (progress) {
      var max = doc.scrollHeight - window.innerHeight;
      progress.style.transform = 'scaleX(' + (max > 0 ? y / max : 0) + ')';
    }
    lastY = y;
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  /* Split headlines into words for the line reveal */
  document.querySelectorAll('[data-split]').forEach(function (el) {
    var i = 0;
    function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span');
            w.className = 'w';
            var inner = document.createElement('span');
            inner.textContent = part;
            inner.style.setProperty('--i', i++);
            w.appendChild(inner);
            frag.appendChild(w);
          });
          child.parentNode.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    }
    el.setAttribute('aria-label', el.textContent.trim());
    walk(el);
    el.classList.add('split');
  });

  /* Stagger index for grouped reveals */
  document.querySelectorAll('[data-stagger]').forEach(function (group) {
    Array.prototype.forEach.call(group.querySelectorAll('.reveal'), function (el, i) {
      el.style.setProperty('--i', i % 8);
    });
  });

  /* Count-up numbers */
  function countUp(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    if (isNaN(target)) return;
    var suffix = el.getAttribute('data-suffix') || '';
    if (reduce) { el.textContent = target + suffix; return; }
    var start = null;
    var dur = 1400;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 4);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  /* Reveal on scroll */
  var targets = document.querySelectorAll('.reveal, .reveal-clip, .split, [data-count], .step, .case-cover');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('visible');
        if (e.target.hasAttribute('data-count')) countUp(e.target);
        io.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (el) { io.observe(el); });
  } else {
    targets.forEach(function (el) {
      el.classList.add('visible');
      if (el.hasAttribute('data-count')) countUp(el);
    });
  }

  /* Hero orbit path lengths */
  document.querySelectorAll('.hero-orbit path:not(.thin)').forEach(function (p) {
    if (p.getTotalLength) p.style.setProperty('--len', Math.ceil(p.getTotalLength()));
  });

  /* Magnetic buttons and pointer spotlight (desktop only) */
  if (finePointer && !reduce) {
    document.querySelectorAll('.magnetic').forEach(function (el) {
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.25;
        var y = (e.clientY - r.top - r.height / 2) * 0.35;
        el.style.transform = 'translate(' + x + 'px,' + y + 'px)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
    document.querySelectorAll('.spot').forEach(function (el) {
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        el.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });
    /* Subtle parallax on hero background */
    var hero = document.querySelector('.hero');
    if (hero) {
      hero.addEventListener('mousemove', function (e) {
        var x = (e.clientX / window.innerWidth - 0.5) * 10;
        var y = (e.clientY / window.innerHeight - 0.5) * 10;
        hero.style.setProperty('--px', x + 'px');
        hero.style.setProperty('--py', y + 'px');
        var orbit = hero.querySelector('.hero-orbit');
        if (orbit) orbit.style.transform = 'translate(' + (-x) + 'px,' + (-y) + 'px)';
      });
    }
  }

  /* Case study filters, with URL hash support (#energy, #events) */
  var filters = document.querySelectorAll('.filter-btn');
  var cases = document.querySelectorAll('.case-card');
  function applyFilter(f) {
    var matched = false;
    filters.forEach(function (b) {
      var on = b.dataset.filter === f;
      if (on) matched = true;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (!matched) f = 'all';
    cases.forEach(function (c) {
      var show = f === 'all' || c.dataset.category === f || c.dataset.sector === f;
      if (show) {
        c.hidden = false;
        c.classList.add('is-filtering');
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(function () { c.classList.remove('is-filtering'); });
        });
      } else {
        c.hidden = true;
      }
    });
    var status = document.querySelector('.filter-status');
    if (status) status.textContent = document.querySelectorAll('.case-card:not([hidden])').length + '';
  }
  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      applyFilter(btn.dataset.filter);
      if (history.replaceState) history.replaceState(null, '', btn.dataset.filter === 'all' ? location.pathname : '#' + btn.dataset.filter);
    });
  });
  if (cases.length && location.hash) {
    var h = location.hash.slice(1);
    var sectorMatch = Array.prototype.some.call(cases, function (c) { return c.dataset.sector === h; });
    if (sectorMatch) {
      cases.forEach(function (c) { c.hidden = c.dataset.sector !== h; });
    } else {
      applyFilter(h);
    }
  }

  /* LinkedIn share + copy link */
  document.querySelectorAll('[data-share="linkedin"]').forEach(function (a) {
    var url = a.getAttribute('data-url') || location.href;
    a.href = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url);
    a.addEventListener('click', function (e) {
      e.preventDefault();
      window.open(a.href, 'li-share', 'width=600,height=640,noopener');
    });
  });
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var label = b.querySelector('span');
      var original = label ? label.textContent : '';
      var done = function () {
        if (label) {
          label.textContent = b.getAttribute('data-copied') || 'Copied';
          setTimeout(function () { label.textContent = original; }, 1800);
        }
      };
      if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(done);
    });
  });

  /* Language switch: remember the visitor's choice */
  document.querySelectorAll('.lang-switch a').forEach(function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('pg-lang', a.getAttribute('hreflang')); } catch (e) {}
    });
  });

  /* Smooth page transitions for internal links */
  if (!reduce) {
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
      if (a.hasAttribute('data-share') || a.hasAttribute('download')) return;
      var href = a.getAttribute('href');
      if (!href || href.charAt(0) === '#' || /^(mailto|tel|javascript):/.test(href)) return;
      if (a.host !== location.host) return;
      if (a.pathname === location.pathname && a.hash) return;
      e.preventDefault();
      document.body.classList.add('is-leaving');
      setTimeout(function () { location.href = a.href; }, 260);
    });
    window.addEventListener('pageshow', function (e) {
      if (e.persisted) document.body.classList.remove('is-leaving');
    });
  }

  /* Contact form */
  var form = document.querySelector('#contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      var submit = form.querySelector('button[type="submit"]');
      var endpoint = form.getAttribute('data-endpoint');
      if (form.querySelector('.hp input') && form.querySelector('.hp input').value) { e.preventDefault(); return; }
      if (form.getAttribute('action') && !endpoint) return; // let WordPress handle the POST
      e.preventDefault();
      submit.disabled = true;
      submit.textContent = form.getAttribute('data-sending') || 'Sending...';
      var finish = function () {
        submit.textContent = form.getAttribute('data-thanks') || 'Thank you. We will be in touch.';
      };
      if (endpoint) {
        fetch(endpoint, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
          .then(finish).catch(function () { submit.disabled = false; submit.textContent = 'Error. Please email us.'; });
      } else {
        setTimeout(finish, 600);
      }
    });
  }

  /* Cookie consent. LinkedIn Insight Tag only loads after acceptance. */
  var banner = document.querySelector('.cookie');
  function loadInsightTag() {
    var pid = cfg.linkedinPartnerId;
    if (!pid || window._linkedin_data_partner_ids) return;
    window._linkedin_partner_id = pid;
    window._linkedin_data_partner_ids = [pid];
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://snap.licdn.com/li.lms-analytics/insight.min.js';
    document.head.appendChild(s);
  }
  var consent = null;
  try { consent = localStorage.getItem('pg-consent'); } catch (e) {}
  if (consent === 'yes') loadInsightTag();
  if (banner && cfg.linkedinPartnerId && !consent) {
    setTimeout(function () { banner.classList.add('show'); }, 1200);
    banner.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      var yes = b.classList.contains('ok');
      try { localStorage.setItem('pg-consent', yes ? 'yes' : 'no'); } catch (err) {}
      if (yes) loadInsightTag();
      banner.classList.remove('show');
    });
  }
})();
