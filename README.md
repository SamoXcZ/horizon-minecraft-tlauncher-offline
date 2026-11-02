# Horizon — Minecraft 26.3 in Rust, run on macOS Intel from TLauncher files

> **STATUS: ABANDONED mid-fix.** The game runs, plays, and saves. The last work session
> tuned performance and mapped the remaining world-gen bug. Not finished.

Horizon is an independent Rust re-implementation of Minecraft Java Edition. This project
packages what was needed to **run it on macOS Intel** with **no Microsoft account** (offline /
cracked style) using the **Minecraft files TLauncher already has**.

## What works (verified)

- Horizon nightly `2026-11-01-c9d474d` (x86_64, Metal) runs on an Intel Iris 6000 Mac.
- Minecraft 26.3 resources prepared from TLauncher-style files (client jar, server jar, 114
  libraries, ~5,147 assets, sounds, languages).
- Offline session starts via the game binary directly (no launcher auth gate).
- **Performance: FIXED during this session** (benchmarked):
  - Before: avg FPS ~30–55, worst frame ~1 s.
  - After (graphics preset `performance`, render distance 8, max FPS 60, VSync off): avg FPS
    **81–116**, worst frame ~75 ms.

## How to run

```sh
./play.sh                 # Steve, TLauncher folder as game dir, passes args through
./play.sh --world "New World" --render-distance 8
```

Environment:
- `OXIDE_TLAUNCHER_DIR` — TLauncher's game folder (default `~/Library/Application Support/minecraft`)
- `HORIZON_NAME` — offline player name (default `Steve`)
- `HORIZON_GAME_DIR` — where saves live (default: TLauncher folder)
- `HORIZON_HOME` — Horizon's data folder (default: `./home`)

## Known unfinished bug

- Trees sometimes don't spawn / spawn weirdly; player can fall through trees/terrain.
- Source-level hunt performed in `crates/horizon-world` (tree placement, collision, block-state
  facts). Root cause not fixed. A full rebuild was required to fix it, which was not completed here.

## Finish it

If you have a beefier machine and ~30+ GB free disk:

1. Free space, then build the Horizon workspace from source.
2. Continue the worldgen/collision fix identified in the source hunt.

This is a snapshot in progress — pull requests welcome, bug reports welcome, finishers wanted.
