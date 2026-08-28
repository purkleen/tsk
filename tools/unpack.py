#!/usr/bin/env python3
"""Unpack a self-extracting bundled page into a plain static site.

The bundle stores every asset as base64 (optionally gzipped) in a
`__bundler/manifest` script tag, and the real document in a
`__bundler/template` tag with each asset referenced by UUID. At runtime the
page decodes the manifest into blob: URLs and string-replaces the UUIDs.

This script does the same substitution ahead of time, writing assets to disk
and rewriting the template to point at them, so the result is an ordinary
directory of files that a static server can host.

Usage: python3 tools/unpack.py sprout.html src
"""

import base64
import gzip
import json
import os
import re
import shutil
import sys

EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "font/woff2": ".woff2",
    "text/javascript": ".js",
    "text/css": ".css",
    "text/html": ".html",
}

# Bundled copies of things the page originally loaded from a CDN.
VENDOR = {
    "https://unpkg.com/react@18.3.1/umd/react.production.min.js": "vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js": "vendor/react-dom.production.min.js",
    "https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700"
    "&family=Nunito:wght@400;500;600;700;800&display=swap": "fonts/google-fonts.css",
}

# UUID-named scripts that are easier to recognise under a real name.
RENAME = {
    "e81c1272-eaf4-4a53-8963-be77334e53e2": "vendor/dc-runtime.js",
    "0936499c-1029-4189-8ec4-7203e1198744": "vendor/image-slot.js",
}


def section(src, tag):
    start = src.index('<script type="__bundler/%s">' % tag)
    start = src.index(">", start) + 1
    return src[start:src.index("</script>", start)]


def main(bundle_path, out_dir):
    src = open(bundle_path, encoding="utf-8").read()
    manifest = json.loads(section(src, "manifest"))
    template = json.loads(section(src, "template"))
    ext_resources = json.loads(section(src, "ext_resources"))
    ident_of = {e["uuid"]: e["id"] for e in ext_resources}

    for d in ("assets", "fonts", "vendor", "components"):
        os.makedirs(os.path.join(out_dir, d), exist_ok=True)

    paths = {}         # uuid -> path relative to out_dir
    resource_map = {}  # original id -> path, for window.__resources
    for uuid, entry in manifest.items():
        ident = ident_of.get(uuid)
        if ident in VENDOR:
            path = VENDOR[ident]
        elif ident == "./PostCard.dc.html":
            path = "components/PostCard.dc.html"
        elif ident and not ident.startswith(("http", "./")):
            path = "assets/%s%s" % (ident, EXT.get(entry["mime"], ""))
        else:
            # Unnamed entries are the font files the Google Fonts CSS points at.
            path = "fonts/%s%s" % (uuid[:8], EXT.get(entry["mime"], ""))
        paths[uuid] = path
        if ident:
            resource_map[ident] = path

        raw = base64.b64decode(entry["data"])
        if entry.get("compressed"):
            raw = gzip.decompress(raw)
        open(os.path.join(out_dir, path), "wb").write(raw)

    for uuid, nice in RENAME.items():
        if uuid in paths:
            shutil.move(os.path.join(out_dir, paths[uuid]), os.path.join(out_dir, nice))
            paths[uuid] = nice

    out = template
    for uuid, path in paths.items():
        out = out.replace(uuid, path)

    # The runtime resolves sub-component and image-slot sources through this
    # map, exactly as the bundle's loader built it from blob: URLs.
    head = re.search(r"<head[^>]*>", out, re.I)
    inject = "\n<title>Sprout</title>\n<script>window.__resources = %s;</script>" % json.dumps(
        resource_map
    )
    out = out[: head.end()] + inject + out[head.end():]

    # SRI hashes covered the CDN copies; they no longer match local files, and
    # crossorigin would force a needless CORS fetch.
    out = re.sub(r'\s+integrity="[^"]*"', "", out, flags=re.I)
    out = re.sub(r'\s+crossorigin="[^"]*"', "", out, flags=re.I)

    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(out)

    # PostCard's helmet is injected into the main document, so its relative
    # script src resolves against the page root rather than components/.
    card = os.path.join(out_dir, "components/PostCard.dc.html")
    if os.path.exists(card):
        text = open(card, encoding="utf-8").read()
        open(card, "w", encoding="utf-8").write(
            text.replace('src="./image-slot.js"', 'src="vendor/image-slot.js"')
        )

    print("wrote %s (%d assets, %d mapped resources)" % (out_dir, len(manifest), len(resource_map)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sprout.html",
         sys.argv[2] if len(sys.argv) > 2 else "src")
