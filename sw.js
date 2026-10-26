/* Calendario laboral 2027 - service worker (generado por build.py desde sw.src.js) */
'use strict';
var VERSION = 'cl27-7f51a05124';
var SHELL = ["/", "/app.css?v=d9af9384b2", "/app.js?v=f433d3c1c5", "/manifest.webmanifest", "/icons/icon-192.png", "/icons/icon-512.png"];
var SCOPE = self.registration.scope;

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k.indexOf('cl27-') === 0 && k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

// Cache-first para esta carpeta; la red refresca la copia en segundo plano.
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || req.url.indexOf(SCOPE) !== 0) return;
  var nav = req.mode === 'navigate';
  var url = new URL(req.url);
  if (/\/(ads|robots)\.txt$|\.xml$/.test(url.pathname)) return; // siempre de la red, nunca en caché
  var key = nav ? url.origin + url.pathname : req;
  var net = caches.open(VERSION).then(function (c) {
    return fetch(req).then(function (res) {
      if (res && res.ok && res.type === 'basic') c.put(key, res.clone());
      return res;
    });
  });
  e.respondWith(caches.open(VERSION).then(function (c) {
    return c.match(key).then(function (hit) {
      return hit || net.catch(function () { return nav ? c.match(SCOPE) : Response.error(); });
    });
  }));
  e.waitUntil(net.catch(function () {}));
});
