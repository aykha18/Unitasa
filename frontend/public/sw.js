// Service Worker v4 - Port Change & Protocol Fix
const CACHE_NAME = 'auto-mark-landing-v4';
const STATIC_CACHE = 'auto-mark-static-v4';
const DYNAMIC_CACHE = 'auto-mark-dynamic-v4';
const API_CACHE = 'auto-mark-api-v4';

// Critical resources to cache immediately
const urlsToCache = [
  '/',
  '/manifest.json',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

// Resources to cache on first request
const dynamicCacheUrls = [
  '/static/js/',
  '/static/css/',
  '/static/media/',
  'https://fonts.gstatic.com/'
];

// API endpoints to cache with network-first strategy
const apiCacheUrls = [
  '/api/v1/crm-marketplace/',
  '/api/v1/landing/'
];

// Install event - cache critical resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => {
        return cache.addAll(urlsToCache);
      }),
      caches.open(DYNAMIC_CACHE),
      caches.open(API_CACHE)
    ]).catch((error) => {
      console.log('Cache install failed:', error);
    })
  );

  // Skip waiting to activate immediately
  self.skipWaiting();
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignore requests that are not http or https (e.g. chrome-extension://)
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Handle API requests with network-first strategy
  if (apiCacheUrls.some(apiUrl => request.url.includes(apiUrl))) {
    event.respondWith(networkFirstStrategy(request, API_CACHE));
    return;
  }

  // Handle static assets with cache-first strategy
  if (request.destination === 'script' ||
    request.destination === 'style' ||
    request.destination === 'image' ||
    dynamicCacheUrls.some(dynamicUrl => request.url.includes(dynamicUrl))) {
    event.respondWith(cacheFirstStrategy(request, DYNAMIC_CACHE));
    return;
  }

  // Handle navigation requests with network-first, fallback to cache
  if (request.destination === 'document') {
    event.respondWith(networkFirstStrategy(request, STATIC_CACHE));
    return;
  }

  // Skip caching for API requests - let them go directly to network
  if (request.url.includes('/api/')) {
    return;
  }

  // Default: try cache first, then network
  event.respondWith(
    caches.match(request)
      .then((response) => {
        return response || fetch(request);
      })
      .catch(() => {
        // Offline fallback
        if (request.destination === 'document') {
          return caches.match('/');
        }
      })
  );
});

// Activate event - clean up old caches and claim clients
self.addEventListener('activate', (event) => {
  const currentCaches = [STATIC_CACHE, DYNAMIC_CACHE, API_CACHE];

  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (!currentCaches.includes(cacheName)) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Claim all clients immediately
      self.clients.claim()
    ])
  );
});

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'assessment-submission') {
    event.waitUntil(syncAssessmentData());
  }
});

async function syncAssessmentData() {
  try {
    const assessmentData = await getStoredAssessmentData();
    if (assessmentData) {
      await fetch('/api/v1/landing/assessment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assessmentData)
      });
      await clearStoredAssessmentData();
    }
  } catch (error) {
    console.log('Background sync failed:', error);
  }
}

async function getStoredAssessmentData() {
  return new Promise((resolve) => {
    const request = indexedDB.open('AutoMarkDB', 1);
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['assessments'], 'readonly');
      const store = transaction.objectStore('assessments');
      const getRequest = store.get('pending');
      getRequest.onsuccess = () => resolve(getRequest.result);
    };
  });
}

async function clearStoredAssessmentData() {
  return new Promise((resolve) => {
    const request = indexedDB.open('AutoMarkDB', 1);
    request.onsuccess = (event) => {
      const db = event.target.result;
      const transaction = db.transaction(['assessments'], 'readwrite');
      const store = transaction.objectStore('assessments');
      store.delete('pending');
      transaction.oncomplete = () => resolve();
    };
  });
}
// Caching strategies
async function cacheFirstStrategy(request, cacheName) {
  try {
    // Only handle http/https requests
    if (!request.url.startsWith('http')) {
      return fetch(request);
    }

    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok && request.method === 'GET') {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Cache-first strategy failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirstStrategy(request, cacheName) {
  try {
    // Only handle http/https requests
    if (!request.url.startsWith('http')) {
      return fetch(request);
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok && request.method === 'GET') {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response('Offline', { status: 503 });
  }
}

// Cache size management
async function manageCacheSize(cacheName, maxItems) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();

  if (keys.length > maxItems) {
    const itemsToDelete = keys.slice(0, keys.length - maxItems);
    await Promise.all(itemsToDelete.map(key => cache.delete(key)));
  }
}

// Periodic cache cleanup
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CLEANUP_CACHE') {
    event.waitUntil(
      Promise.all([
        manageCacheSize(DYNAMIC_CACHE, 50),
        manageCacheSize(API_CACHE, 20)
      ])
    );
  }
});