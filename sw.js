/* Calendario laboral 2027 - service worker (generado por build.py desde sw.src.js) */
'use strict';
var VERSION = 'cl27-v4-511f236022';
var SHELL = ["/app.css?v=eb532e2cd5", "/app.js?v=f8301c3202", "/manifest.webmanifest", "/icons/icon-192.png", "/icons/icon-512.png"];
var SCOPE = self.registration.scope;

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k.indexOf('cl27-') === 0 && k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

// Páginas: siempre de la red (copia solo para ir sin conexión). css/js/imágenes: caché primero (llevan ?v=).
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || req.url.indexOf(SCOPE) !== 0) return;
  var url = new URL(req.url);
  if (/\/(ads|robots)\.txt$|\.xml$|\.ics$|\.csv$/.test(url.pathname)) return; // siempre de la red
  if (req.mode === 'navigate') {
    var key = url.origin + url.pathname;
    e.respondWith(fetch(req).then(function (res) {
      if (res && res.ok && res.type === 'basic') { var cp = res.clone(); caches.open(VERSION).then(function (c) { c.put(key, cp); }); }
      return res;
    }).catch(function () {
      return caches.open(VERSION).then(function (c) { return c.match(key).then(function (hit) { return hit || Response.error(); }); });
    }));
    return;
  }
  e.respondWith(caches.open(VERSION).then(function (c) {
    return c.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        if (res && res.ok && res.type === 'basic') c.put(req, res.clone());
        return res;
      });
    });
  }));
});
