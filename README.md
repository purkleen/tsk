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
tools/unpack.py          regenerates the app files in public/

public/index.html        the app: markup with {{ }} bindings + a DCLogic class
public/components/       PostCard.dc.html, a sub-component
public/vendor/           dc-runtime.js, image-slot.js, React 18.3.1 UMD
public/assets/           post photos (p01–p11) and avatars
public/fonts/            Fredoka + Nunito woff2, and the @font-face CSS

public/dashboard.html    hand-authored — see below
public/fonts/fonts.css   hand-authored — latin @font-face rules for it
```

## Dashboard

`public/dashboard.html` is a scaffold for a parent home screen, at
http://localhost:4173/dashboard.html. It follows a wireframe, top to bottom:

| Block | Notes |
| --- | --- |
| Greeting + avatar | Two lines — "Good morning," then the name |
| Announcements and upcoming events | A stack, one card at a time; the layers peeking below stand for what is queued, and retract as it empties |
| Upcoming events · Due payments | Two-up row of tall cards |
| Useful links | Four tiles — three plus a "More" |
| *fold* | Everything above fits a 402×874 phone without scrolling |
| Children feed | Full-width list |
| Events | Full-width list |

The announcement stack is driven by the `items` array in the script at the
bottom of the file — add or remove entries there and the dots and peeking
layers follow automatically.

It is deliberately *not* built on the DC runtime. `index.html` is generated
output — 3,500 lines of inline styles and `{{ }}` bindings — so editing it by
hand is unpleasant and any change is lost on the next unpack. The dashboard is
plain HTML and CSS with the app's colours, spacing, and shadows named as custom
properties at the top of the file, so it can be edited directly.

It reuses the app's own font files via `public/fonts/fonts.css` (the latin
subset lifted from `index.html`, so it adds no download weight) and shares the
`assets/` images. The phone frame collapses below 520px, so it also works
full-bleed on a real device.

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

It is deterministic: every file it generates matches the committed copy byte for
byte. It only ever writes the files it owns, so the two hand-authored files
listed above survive a re-run — but it will overwrite edits made directly to
`index.html` or anything else it generates.

## Notes

Two harmless 404s appear in the console and are inherent to the original
bundle: `.image-slots.state.json` (the image-slot component probing for saved
state) and `{{ creatorExampleSrc }}` (the browser eagerly fetching an
attribute before the runtime hydrates it).

`public/vendor/dc-runtime.js` is a generated build artifact — edit the app in
`public/index.html`, not there.
