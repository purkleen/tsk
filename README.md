# Sprout

A preschool family-communication app prototype — class feed, messaging, events,
tuition reminders, and milestone capture — with a parent/teacher role switch.

This repo is the unpacked, runnable source of `sprout.html`, a single-file
self-extracting bundle. Everything runs offline; there are no CDN requests and
no build step.

## Run it

```bash
python3 -m http.server 4173 --directory src
```

Then open http://localhost:4173. It must be served over HTTP — opening
`src/index.html` as a `file://` URL will not work, because the runtime fetches
the component and asset files.

## Layout

```
sprout.html              original self-extracting bundle (2.9 MB)
tools/unpack.py          regenerates src/ from the bundle
src/index.html           the app: markup with {{ }} bindings + a DCLogic class
src/components/          PostCard.dc.html, a sub-component
src/vendor/              dc-runtime.js, image-slot.js, React 18.3.1 UMD
src/assets/              post photos (p01–p11) and avatars
src/fonts/               Fredoka + Nunito woff2, and the @font-face CSS
```

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
python3 tools/unpack.py sprout.html src
```

It is deterministic: the output matches the committed `src/` byte for byte.

## Notes

Two harmless 404s appear in the console and are inherent to the original
bundle: `.image-slots.state.json` (the image-slot component probing for saved
state) and `{{ creatorExampleSrc }}` (the browser eagerly fetching an
attribute before the runtime hydrates it).

`src/vendor/dc-runtime.js` is a generated build artifact — edit the app in
`src/index.html`, not there.
