/* Tradepsy service worker.

   Two jobs, no more. It makes the app installable (a fetch handler is part of
   what a browser looks for before it will offer installation), and it keeps the
   app openable with the network switched off or the machine airplaned.

   Nothing about your journal passes through here. Accounts, trades, routines
   and reports live in this origin's local storage, which the service worker
   never reads or writes. This caches the program, not the data. */

/* Bumped whenever the shell list changes, so an old cache is thrown away
   rather than kept alongside the new one. */
const VERSION = "tradepsy-v2";
const SHELL = [
    "./",
    "./tradepsy.html",
    "./manifest.webmanifest",
    "./icons/icon-192.png",
    "./icons/icon-256.png",
    "./icons/icon-384.png",
    "./icons/icon-512.png",
    "./icons/icon-maskable-192.png",
    "./icons/icon-maskable-512.png",
    "./icons/apple-touch-icon.png",
    "./icons/favicon-32.png",
];

self.addEventListener("install", (event) => {
    /* One missing file must not fail the whole install — a bundle that was
       copied without the icons should still go offline-capable. */
    event.waitUntil(caches.open(VERSION)
        .then((cache) => Promise.all(SHELL.map((url) => cache.add(url).catch(() => null))))
        .then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
    event.waitUntil(caches.keys()
        .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
        .then(() => self.clients.claim()));
});

self.addEventListener("message", (event) => {
    if (event.data === "skip-waiting")
        self.skipWaiting();
});

self.addEventListener("fetch", (event) => {
    const request = event.request;
    if (request.method !== "GET")
        return;
    const url = new URL(request.url);
    if (url.origin !== self.location.origin)
        return;

    /* Navigations get the cached page first. The app is a single file with no
       server behind it, so "fresh" is a meaningless idea here and a network
       round trip only adds a spinner when the machine is offline. */
    if (request.mode === "navigate") {
        event.respondWith(caches.match("./tradepsy.html")
            .then((hit) => hit || caches.match("./").then((root) => root || fetch(request))));
        return;
    }

    event.respondWith(caches.match(request).then((hit) => {
        if (hit)
            return hit;
        return fetch(request).then((res) => {
            /* Opaque and error responses are not worth keeping: caching them
               turns a one-off failure into a permanent one. */
            if (!res || res.status !== 200 || res.type !== "basic")
                return res;
            const copy = res.clone();
            caches.open(VERSION).then((cache) => cache.put(request, copy)).catch(() => null);
            return res;
        }).catch(() => hit);
    }));
});
