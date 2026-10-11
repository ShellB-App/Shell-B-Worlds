# Shell:B Worlds

[![Validate](https://github.com/ShellB-App/Shell-B-Worlds/actions/workflows/validate.yml/badge.svg)](https://github.com/ShellB-App/Shell-B-Worlds/actions/workflows/validate.yml) [![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Community worlds for [Shell:B](https://github.com/ShellB-App/Shell-B), the local-first AI workspace.
Part of the family with [Shell-B-Themes](https://github.com/ShellB-App/Shell-B-Themes), [Shell-B-Screensavers](https://github.com/ShellB-App/Shell-B-Screensavers) and [Shell-B-Agents](https://github.com/ShellB-App/Shell-B-Agents).

A Shell:B world is **a guided tour and a set of places on one of the worlds in the Worlds app**: Earth, the Moon,
Mars, the moons of the giant planets, the dwarf planets. A tour is a list of stops the app flies between while the
narration is shown and, if you like, read aloud. A place is a pin with its own card: a summary, facts, sections and
links, in the *Atlas places* layer. An overlay is a GeoJSON file drawn on the map: a route, a boundary, a set of
points. Everything is data; a world can't run code.

## Install one

Today a world plays through the chat. Print its map block and paste it into any conversation with Atlas or Shell:B:

```bash
python3 -I scripts/map_block.py apollo-sites
```

The block renders as a map card; *Open in Worlds* flies to the scene, and *Play tour* starts the fly-through. For a
world's places, ask Atlas to add them ("add the places from this world to the map") and it will write them to the cards
with `annotate_map_feature`. Overlays import through **Worlds → Bookmarks → Import** (GeoJSON, KML or GPX).

One-click install from Settings, the way themes and screensavers work, is planned; the files here already have the
shape the app reads, so nothing will need to change.

## Catalogue

| World | Body | What it is |
|---|---|---|
| The Apollo landing sites | Moon | Six landings, 1969 to 1972, plus Surveyor 3 as a place |
| Every landing on Mars | Mars | Ten landers and rovers from Viking 1 to Zhurong |
| Ring of Fire | Earth | Nine volcanoes around the Pacific rim; turn on the earthquake layer |
| The Silk Road | Earth | Xi'an to Constantinople in nine cities, with the road as a GeoJSON overlay |

`index.json` is the machine-readable version of this table.

## Make one

Ask Atlas for a tour ("give me a tour of the Jupiter missions") and save the block's `tour` list into a `world.json`,
or write it by hand. Every world is a folder under `worlds/`:

```
worlds/silk-road/
  world.json       the world
  route.geojson    optional overlays, listed in world.json
  preview.jpg      optional, about 640×360, ≤ 400 KB
```

The format:

```jsonc
{
  "name": "The Silk Road",                   // 1-60 characters
  "blurb": "One or two sentences for the picker (≤ 200 characters)",
  "body": "earth",                           // sol, mercury, venus, earth, moon, mars, vesta, ceres, jupiter, io, europa,
                                             // ganymede, callisto, saturn, enceladus, titan, …, uranus, neptune, pluto, …
  "scene": {                                 // optional: where the world opens
    "lat": 38, "lon": 72, "zoom": 3.1, "pitch": 0, "bearing": 0,
    "layers": {"relief": true, "quakes": true},   // layer ids: flights, satellites, quakes, daynight, imagery, radar,
                                             // aurora, wind, landmarks, traverses, wonders, shipwrecks, caves, neolithic,
                                             // launchsites, webcams, places, relief, terrain3d, buildings, iceage,
                                             // atmosphere, plumes, dust, grid, stars
    "time": "1969-07-20T20:17:00Z",          // optional: sets the map clock
    "years_ago": 20000                       // optional: the Ice Age coast
  },
  "tour": [                                  // up to 60 stops
    {"title": "Xi'an", "text": "20 to 1200 characters, read aloud", "lat": 34.34, "lon": 108.94,
     "zoom": 9, "pitch": 45, "bearing": 280, "seconds": 14}
  ],
  "places": [                                // up to 200 pins with cards
    {"name": "Surveyor 3", "lat": -2.99, "lon": -23.34, "kind": "mission",   // place, mission, crater, volcano, mountain,
     "summary": "…", "facts": ["…"],          // canyon, plain, sea, site, city, wreck, wonder, event, route
     "sections": [{"title": "…", "text": "…"}], "links": [{"title": "…", "url": "https://…"}]}
  ],
  "overlays": ["route.geojson"],             // GeoJSON files in the folder, ≤ 2 MB each
  "author": "Your name",
  "license": "CC-BY-4.0",                    // an SPDX id; CC-BY-4.0 suits text you wrote, CC0-1.0 if you don't care
  "version": "1.0",
  "tags": ["earth", "history"]
}
```

Longitudes are east-positive, from -180 to 180 (the app also accepts 0 to 360 for the planetary bodies).

A good tour reads like a documentary, not an encyclopaedia: each stop says what happened here and why it matters, in
two to four sentences that sound right read aloud. Check every coordinate on the map before you commit; the validator
can tell a number is in range, not that it is the right crater.

Then check it:

```bash
python3 -I scripts/validate.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the pull request checklist.

## Other collections

Shell:B installs from the whole family: [Shell-B-Themes](https://github.com/ShellB-App/Shell-B-Themes), [Shell-B-Screensavers](https://github.com/ShellB-App/Shell-B-Screensavers) and [Shell-B-Agents](https://github.com/ShellB-App/Shell-B-Agents) work the same way, with a validator, CI and a one-screen checklist each. Found a bug in the app itself? That goes to [Shell-B issues](https://github.com/ShellB-App/Shell-B/issues); questions and show-and-tell to [Discussions](https://github.com/ShellB-App/Shell-B/discussions).

## License

The scripts and this repository are MIT. Each world names its own license in `world.json`; the ones here are CC-BY-4.0.
