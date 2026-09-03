# Sprout

A preschool family-communication app prototype — class feed, messaging, events,
tuition reminders, and milestone capture — with a parent/teacher role switch.

This repo is the unpacked, runnable source of `sprout.html`, a single-file
self-extracting bundle. Everything runs offline; there are no CDN requests and
no build step.

## Run it

```bash
python3 -m http.server 4173 --directory public
```

Then open http://localhost:4173. It must be served over HTTP — opening
`public/index.html` as a `file://` URL will not work, because the runtime fetches
the component and asset files.

## Layout

```
sprout.html              original self-extracting bundle (2.9 MB)
tools/unpack.py          regenerates public/ from the bundle
public/index.html        the app: markup with {{ }} bindings + a DCLogic class
public/components/       PostCard.dc.html, a sub-component
public/vendor/           dc-runtime.js, image-slot.js, React 18.3.1 UMD
public/assets/           post photos (p01–p11) and avatars
public/fonts/            Fredoka + Nunito woff2, and the @font-face CSS
```

## Deploying

The site is plain static files with no build step, so any static host works.
It lives in `public/` rather than the repo root, because the root also holds
the original bundle and the unpack script.

`vercel.json` names that directory explicitly:

```json
{ "outputDirectory": "public" }
```

Without it Vercel serves the repo root, finds no `index.html`, and returns 404.
Every path inside `index.html` is relative, so the site works unchanged
wherever `public/` is mounted.

## How the bundle works

`sprout.html` stores every asset base64-encoded (and gzipped) in a
`<script type="__bundler/manifest">` tag, and the real document in a
`__bundler/template` tag where each asset is referenced by UUID. On load, the
page decodes the manifest into `blob:` URLs, string-replaces the UUIDs in the
template, and swaps in the resulting document.

`tools/unpack.py` performs that substitution ahead of time — writing assets to
disk and rewriting the template to point at them — so the result is an ordinary
static site. Re-run it any time:

```bash
python3 tools/unpack.py sprout.html public
```

It is deterministic: the output matches the committed `public/` byte for byte.

## Notes

Two harmless 404s appear in the console and are inherent to the original
bundle: `.image-slots.state.json` (the image-slot component probing for saved
state) and `{{ creatorExampleSrc }}` (the browser eagerly fetching an
attribute before the runtime hydrates it).

`public/vendor/dc-runtime.js` is a generated build artifact — edit the app in
`public/index.html`, not there.
