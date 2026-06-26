const CACHE_NAME = 'nanco-pwa-cache-v1';
const ASSETS = [
  './',
  './index.html',
  './style.css',
  './light-logo.png',
  './dark-logo.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      return cachedResponse || fetch(event.request);
    })
  );
});
