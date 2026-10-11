#!/usr/bin/env python3
"""Check every world in worlds/<id>/world.json and build index.json.

A world is a guided tour and a set of places on one of Shell:B's worlds (Earth, the Moon, Mars, the moons of the
giants…), optionally with GeoJSON overlays. This script checks what the Worlds app would reject: an unknown body,
coordinates off the map, a tour stop without a title or text, a place kind the card layer doesn't know, an overlay
that isn't GeoJSON. Standard library only; run from the repository root:

    python3 -I scripts/validate.py          # check + rebuild index.json
    python3 -I scripts/validate.py --check  # check only (CI); exits 1 on any error
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ROOT / "worlds"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,39}$")
URL_RE = re.compile(r"^https?://[^\s\"'<>]{1,300}$")
BODIES = ("sol", "mercury", "venus", "earth", "moon", "mars", "phobos", "deimos", "vesta", "ceres", "jupiter", "io", "europa",
          "ganymede", "callisto", "saturn", "mimas", "enceladus", "tethys", "dione", "rhea", "titan", "iapetus", "uranus",
          "miranda", "ariel", "umbriel", "titania", "oberon", "neptune", "triton", "pluto", "charon", "haumea", "makemake", "eris")
LAYERS = ("flights", "satellites", "quakes", "daynight", "imagery", "radar", "aurora", "wind", "landmarks", "traverses", "wonders",
          "shipwrecks", "caves", "neolithic", "launchsites", "webcams", "places", "relief", "terrain3d", "buildings", "iceage",
          "atmosphere", "plumes", "dust", "grid", "stars")
PLACE_KINDS = ("place", "mission", "crater", "volcano", "mountain", "canyon", "plain", "sea", "site", "city", "wreck", "wonder", "event", "route")
OVERLAY_EXT = (".geojson", ".json")
MAX_OVERLAY = 2 * 2**20
PREVIEWS = (".jpg", ".jpeg", ".png", ".webp")


def _num(v, lo, hi) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi


def _coords(d: dict, where: str, errors: list[str], body: str):
    if not _num(d.get("lat"), -90, 90):
        errors.append(f"{where}: lat must be a number from -90 to 90")
    if not _num(d.get("lon"), -180, 360):
        errors.append(f"{where}: lon must be a number from -180 to 360 (east-positive)")
    for k, lo, hi in (("zoom", 0, 22), ("pitch", 0, 75), ("bearing", -360, 360)):
        if k in d and not _num(d[k], lo, hi):
            errors.append(f"{where}: {k} must be a number from {lo} to {hi}")
    if "body" in d and d["body"] not in BODIES:
        errors.append(f"{where}: body {d['body']!r} is not a Shell:B world")


def _geojson(path: Path, errors: list[str]):
    if path.stat().st_size > MAX_OVERLAY:
        errors.append(f"overlay {path.name}: larger than {MAX_OVERLAY // 2**20} MB")
        return
    try:
        g = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        errors.append(f"overlay {path.name}: not valid JSON: {e}")
        return
    if not isinstance(g, dict) or g.get("type") not in ("FeatureCollection", "Feature"):
        errors.append(f"overlay {path.name}: must be a GeoJSON Feature or FeatureCollection")


def check(path: Path) -> tuple[dict | None, list[str], list[str]]:
    """(world, errors, warnings). Errors block a merge; warnings are worth a look."""
    errors, warnings = [], []
    try:
        spec = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        return None, [f"not valid JSON: {e}"], []
    if not isinstance(spec, dict):
        return None, ["the file must hold one object"], []
    folder = path.parent.name
    if not ID_RE.match(folder):
        errors.append(f"folder name {folder!r}: lowercase letters, digits and dashes only")
    if spec.get("id") not in (None, folder):
        errors.append(f"id {spec.get('id')!r} doesn't match the folder name {folder!r}")
    name = str(spec.get("name") or "").strip()
    if not name or len(name) > 60:
        errors.append("name: 1-60 characters")
    if not spec.get("blurb") or len(str(spec["blurb"])) > 200:
        errors.append("blurb: 1-200 characters")
    body = spec.get("body")
    if body not in BODIES:
        errors.append(f"body must be one of {', '.join(BODIES)}")
        body = "earth"
    for key in ("author", "license"):
        if not spec.get(key):
            errors.append(f"{key} is required (license: an SPDX id such as MIT or CC-BY-4.0)")
    if not spec.get("version"):
        warnings.append("no version; start at \"1.0\"")

    scene = spec.get("scene")
    if scene is not None:
        if not isinstance(scene, dict):
            errors.append("scene must be an object")
        else:
            if "lat" in scene or "lon" in scene:
                _coords(scene, "scene", errors, body)
            for k, v in (scene.get("layers") or {}).items():
                if k not in LAYERS or not isinstance(v, bool):
                    errors.append(f"scene.layers.{k}: unknown layer or not true/false")
            if "years_ago" in scene and not _num(scene["years_ago"], 0, 80000):
                errors.append("scene.years_ago: 0 to 80000")

    tour = spec.get("tour") or []
    if not isinstance(tour, list):
        errors.append("tour must be a list of stops")
        tour = []
    for i, s in enumerate(tour[:60]):
        where = f"tour[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{where}: a stop is an object")
            continue
        if not str(s.get("title") or "").strip() or len(str(s.get("title"))) > 80:
            errors.append(f"{where}: title 1-80 characters")
        if len(str(s.get("text") or "").strip()) < 20 or len(str(s.get("text"))) > 1200:
            errors.append(f"{where}: text 20-1200 characters (it is read aloud)")
        if "seconds" in s and not _num(s["seconds"], 3, 180):
            errors.append(f"{where}: seconds 3-180")
        _coords(s, where, errors, body)
    if len(tour) > 60:
        errors.append("tour: at most 60 stops")

    places = spec.get("places") or []
    if not isinstance(places, list):
        errors.append("places must be a list")
        places = []
    for i, p in enumerate(places[:200]):
        where = f"places[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{where}: a place is an object")
            continue
        if not str(p.get("name") or "").strip() or len(str(p.get("name"))) > 120:
            errors.append(f"{where}: name 1-120 characters")
        if p.get("kind", "place") not in PLACE_KINDS:
            errors.append(f"{where}: kind must be one of {', '.join(PLACE_KINDS)}")
        _coords(p, where, errors, body)
        if len(str(p.get("summary") or "")) > 1500:
            errors.append(f"{where}: summary at most 1500 characters")
        for j, f in enumerate(p.get("facts") or []):
            if not isinstance(f, str) or not f.strip() or len(f) > 200:
                errors.append(f"{where}.facts[{j}]: a short string")
        for j, sec in enumerate(p.get("sections") or []):
            if not isinstance(sec, dict) or not sec.get("title") or not sec.get("text") or len(str(sec["text"])) > 3000:
                errors.append(f"{where}.sections[{j}]: {{title, text}} with text at most 3000 characters")
        for j, l in enumerate(p.get("links") or []):
            if not isinstance(l, dict) or not l.get("title") or not URL_RE.match(str(l.get("url") or "")):
                errors.append(f"{where}.links[{j}]: {{title, url}} with an http(s) url")
    if len(places) > 200:
        errors.append("places: at most 200")
    if not tour and not places:
        errors.append("a world needs a tour, places, or both")

    overlays = spec.get("overlays") or []
    if not isinstance(overlays, list) or not all(isinstance(o, str) for o in overlays):
        errors.append("overlays: a list of file names in the folder")
        overlays = []
    for o in overlays:
        if "/" in o or o.startswith(".") or Path(o).suffix.lower() not in OVERLAY_EXT:
            errors.append(f"overlay {o!r}: a .geojson file in the world's folder")
        elif not (path.parent / o).is_file():
            errors.append(f"overlay {o!r}: file not found")
        else:
            _geojson(path.parent / o, errors)
    for f in path.parent.iterdir():
        if f.name == "world.json" or f.name in overlays or f.name.startswith("."):
            continue
        if f.stem == "preview" and f.suffix.lower() in PREVIEWS:
            if f.stat().st_size > 400 * 1024:
                errors.append("preview: at most 400 KB")
            continue
        warnings.append(f"{f.name} is not referenced by world.json")
    return spec, errors, warnings


def entry(folder: str, spec: dict, path: Path) -> dict:
    preview = next((f.name for f in path.parent.iterdir() if f.stem == "preview" and f.suffix.lower() in PREVIEWS), None)
    return {
        "id": folder, "name": spec["name"], "blurb": spec["blurb"], "body": spec["body"],
        "stops": len(spec.get("tour") or []), "places": len(spec.get("places") or []), "overlays": len(spec.get("overlays") or []),
        "author": spec["author"], "license": spec["license"], "version": spec.get("version", "1.0"), "tags": spec.get("tags", []),
        "path": str(path.relative_to(ROOT)), "preview": f"worlds/{folder}/{preview}" if preview else None,
    }


def main() -> int:
    check_only = "--check" in sys.argv
    items, failed = [], 0
    files = sorted(WORLDS.glob("*/world.json"))
    if not files:
        print("no worlds found under worlds/<id>/world.json")
        return 1
    for path in files:
        spec, errors, warnings = check(path)
        folder = path.parent.name
        for w in warnings:
            print(f"warning  {folder}: {w}")
        for e in errors:
            print(f"ERROR    {folder}: {e}")
        if errors or spec is None:
            failed += 1
            continue
        items.append(entry(folder, spec, path))
        print(f"ok       {folder} ({spec['name']}: {spec['body']}, {len(spec.get('tour') or [])} stops, {len(spec.get('places') or [])} places)")
    index = {"format": 1, "kind": "world", "items": sorted(items, key=lambda i: i["name"].lower())}
    if not check_only:
        (ROOT / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n")
        print(f"index.json: {len(items)} worlds")
    elif (ROOT / "index.json").exists() and json.loads((ROOT / "index.json").read_text()) != index:
        print("ERROR    index.json is out of date: run scripts/validate.py and commit it")
        failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
