# Contributing a world

1. Fork the repository and add a folder `worlds/<id>/` with a `world.json`. The id is lowercase letters, digits and
   dashes (`apollo-sites`, `ring-of-fire`), and it must not already exist.
2. Fill in `name`, `blurb`, `body`, a `tour` and/or `places`, `author` and `license`. The license is an SPDX id
   (CC-BY-4.0, CC0-1.0, MIT). By opening a pull request you agree that the text is shared under the license you named.
   Text you didn't write yourself must allow redistribution; quote sparingly and say where it comes from.
3. Run `python3 -I scripts/validate.py` from the repository root. Fix every error.
4. Play the tour in your own Shell:B (`scripts/map_block.py <id>` and paste the block) and watch every stop: is the
   camera where it should be, does the narration read well aloud, does it take too long?
5. Commit the folder and the updated `index.json`, and open a pull request describing the world and your sources.

Worlds are reviewed for accuracy and for how they play: right coordinates, narration that earns its seconds, nothing
that reads as advertising. Worlds that are mostly copied text, that promote a business, or that put people's homes on
the map are not merged.

Updating a world: bump `version`, keep the id.
