# Horizon — Minecraft Java Edition 26.3 in Rust, on macOS Intel, offline

> ## Status: **abandoned mid-fix**
>
> The game **runs, plays, saves and performs** in this configuration. A verified world-generation
> defect (trees not spawning / player falling through) was **mapped but not fixed** — see
> *Known issues*. This repository is a snapshot of the working setup plus the fix attempts that were
> in progress.

Horizon is an independent Rust re-implementation of Minecraft: Java Edition. This project packages
everything needed to **run Horizon's Minecraft 26.3 on macOS Intel** — no Microsoft account, offline
mode — using the Minecraft files a TLauncher install already has.

It is not a launcher. It does not contain or reimplement TLauncher's code, ads, telemetry or auth
bypass. It only reuses the *Minecraft files*.

## Legal / disclaimer

- **Horizon** is MIT licensed (upstream project: [horizon-rust/horizon](https://github.com/horizon-rust/horizon)).
- This snapshot is an independent packaging by its author, not an official Horizon release.
- It does **not** include, copy or reproduce any TLauncher proprietary code, assets, telemetry or
  authentication logic. It only consumes publicly distributed Minecraft client/server/library/asset
  bytes fetched from Mojang's public endpoints, plus an open-source Rust game client.
- **Minecraft** and the Minecraft name/logo are trademarks of Mojang Synergies AB and Microsoft.
- Not affiliated with, endorsed by, or connected to Mojang, Microsoft, TLauncher, or any other party.

## Verified working (this snapshot)

| Item | Value |
| --- | --- |
| Game | Horizon Nightly `2026-11-01` · `c9d474d` (Rust, x86_64 Mach-O, Metal) |
| Minecraft version | **26.3** (the version Horizon pins) |
| OS / arch | macOS, **x86_64** (Intel) — verified on **macOS 14.8.1** |
| CPU / GPU | Intel Core i5-5250U @ 1.60 GHz · **Intel(R) Iris(TM) Graphics 6000**, integrated |
| RAM | **4 GB** (shared with the OS) — laptop form factor |
| Display | 1366×768 @ 60 Hz |

The client was started directly (`horizon-client`) with prepared resources, bypassing the launcher's
Microsoft-owner gate entirely. It joins an offline world, generates terrain, renders frames and saves.

### Performance (benchmarked with the built-in `horizon-client --benchmark standard`)

Before tuning:

| Scenario | Avg FPS |
| --- | --- |
| Village | 41.9 |
| Forest | 43.6 |
| Ocean | 30.5 |
| Mountain | 54.3 |

Worst frame time before tuning: **~1 s** (ocean phase); 1% low FPS down to ~1–14.

After tuning (graphics preset `performance`, render distance 8, simulation distance 8, max FPS 60,
VSync off):

| Scenario | Avg FPS |
| --- | --- |
| Village | **109.7** |
| Forest | **81.5** |
| Ocean | **91.0** |
| Mountain | **115.7** |

Worst frame time after: **~75 ms**. Frames per second are now healthy for this hardware.

### What was changed to get there

- `horizon-graphics.txt`: `preset:custom` → `preset:performance`
- `options.txt`: `renderDistance:12 → 8`, `simulationDistance:12 → 8`, `maxFps:120 → 60`,
  `enableVsync:true → false`

## Hardware / OS requirements to run this

- **macOS on Intel (x86_64)** — verified. Metal backend required (Apple Silicon is a different build;
  this snapshot is x86_64 only).
- **Apple GPU with Metal** — verified with Intel Iris integrated graphics.
- **RAM**: verified with 4 GB (tight). 8 GB+ recommended; 4 GB is the floor it survived.
- **Disk**: prepared resources ≈ 1.0 GB, Minecraft files ≈ 683 MB, Horizon install ≈ 200 MB.
- **macOS version**: verified on macOS 14.8.1.

> Devices Horizon did not officially support for this build were made to work here by running the
> x86_64 binary on an Intel Mac with an integrated Iris GPU and driving it through Metal.

## Quick start

```sh
./play.sh                       # Steve, TLauncher folder as game dir
./play.sh --world "New World" --render-distance 8
```

Example — point it at a TLauncher-style folder:

```sh
export OXIDE_TLAUNCHER_DIR="$HOME/Library/Application Support/minecraft"
./play.sh --world "New World" --render-distance 8
```

Environment knobs: `OXIDE_TLAUNCHER_DIR`, `HORIZON_NAME`, `HORIZON_GAME_DIR`, `HORIZON_HOME`.

Minecraft files: `python3 fetch-minecraft-26.3.py <dir> --version-dir <horizon-version-dir>`.

## What a fresh contributor needs (summary)

To get a working setup from scratch:

1. **Horizon** (`nightly-2026-11-01-c9d474d`) + Java 25 runtime — for preparation.
2. **Prepared Horizon resources** — from step 2 above.
3. **Minecraft files** — via `fetch-minecraft-26.3.py`.
4. **`play.sh`** — to launch.

The Python file is only step 3. It's the Minecraft-files fetcher, not the whole setup.

## How to continue from here — the checklist a new contributor needs

Before touching code, a contributor needs all of:

1. **Upstream Horizon repo**: <https://github.com/horizon-rust/horizon>
2. **Which Horizon nightly binary**: `nightly-2026-11-01-c9d474d`, obtained via the Horizon launcher
   release `launcher@0.2.37` (`horizon-launcher-macos-x64.zip`); binaries land in the launcher's
   versions folder. Direct link:
   <https://github.com/horizon-rust/horizon/releases/download/launcher%400.2.37/horizon-launcher-macos-x64.zip>
3. **Rust toolchain**: rustc/cargo **1.99.1** (2026-08-27 / 2026-10-13) — the version used in this session.
4. **Java version**: **Java 25** (Mojang's `java-runtime-epsilon`) — required by the release preparer
   (`horizon-prepare`); the game client itself runs in Rust and does not need a JRE at play time.
5. **`fetch-minecraft-26.3.py`** does: reads the pins from the installed version's
   `research-lock.json` (manifest sha1, client sha1, server sha1), then pulls the pinned version json,
   client jar, server jar, asset index, 114 libraries and ~5,147 asset objects from Mojang's public
   CDN endpoints (piston-meta / piston-data / resources.download.minecraft.net). It verifies sha1s and
   skips files that are already present.
6. **Rough disk for a full build**: the Horizon workspace is large; plan on **30+ GB** of free disk for
   a debug/release build target dir. This session had only ~3.4 GB free and could not build.
7. **Apple Silicon**: this snapshot is **x86_64 only** — Apple Silicon needs the arm64 build. Untested
   for the arm64 path in this session.
8. **What "build from source" requires**: the full Rust workspace (gpui-fast, wgpu, etc.), long compile
   times, substantial disk; not completed in this session.
9. **Direct link to the exact commit used**: <https://github.com/horizon-rust/horizon/commit/c9d474d>
10. **Where the worldgen bug lives** (from the source hunt):
    - `crates/horizon-world/src/worldgen/generator.rs` — `GenBlockStates::get` (~line 132-134) with
      the silent `.unwrap_or_default()` fallback.
    - `crates/horizon-world/src/worldgen/tree_blocks.rs` — `has` (~247-251), `valid_tree_pos` (~259-262).
    - `crates/horizon-world/src/worldgen/tree.rs` — `TreeFeature::place` (~551-601), `do_place` (~603-653),
      clipped-tree skip (~630-633), `max_free_tree_height` (~655-678).
    - Fall-through side: `crates/horizon-world/src/world_movement.rs` — `resolve_world_movement` (~48-95),
      `no_world_collision` (~106-142, empty-shape gate ~120); `crates/horizon-world/src/block_collision*.rs`;
      `crates/horizon-world/src/collision.rs` — `CachedCollisionRegistry::cached_shape` (~243-253);
      client side `crates/horizon-client/src/motion.rs` — `collide` (~2277-2291).

## Known issues (the unfinished work)

1. **World generation defects (unfixed, being worked):**
   - Trees sometimes do not spawn correctly / strangely.
   - Player can fall through trees / terrain.
   - Source-level cause mapped to block-state fact handling in `horizon-world` (generator/collision);
     fix requires a full rebuild, which was not completed in this session.

2. **Performance**: fixed via preset tuning; residual frame jitter remained at the margin.

3. **Offline only**: no skins, Realms, or authenticated servers.

## For contributors / finishers

To go from zero to playing on a fresh machine:

1. Install the Horizon launcher and the `nightly-2026-11-01-c9d474d` build (x86_64).
2. Prepare the resources: `horizon-prepare` with Java 25 (release preparer).
3. Fetch the Minecraft files: `python3 fetch-minecraft-26.3.py <minecraft-dir> --version-dir <horizon-version-dir>`.
4. Run: `./play.sh`.

Then continue the worldgen/collision fix identified during the source hunt.

---

*This is a fan-made, abandoned-in-progress snapshot. Not affiliated with or endorsed by Mojang, Microsoft.*
