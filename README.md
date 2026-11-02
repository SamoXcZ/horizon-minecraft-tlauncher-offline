# Horizon — Minecraft Java Edition 26.3 in Rust, on macOS Intel, offline

> ## Status: **abandoned mid-fix**
>
> The game **runs, plays, saves and performs** in this configuration. A verified world-generation
> defect (trees not spawning / player falling through) was **mapped but not fixed** — see
> *Known issues*. This repository is a snapshot of the working setup plus the fix attempts that were
> in progress.

Horizon is an independent Rust re-implementation of Minecraft: Java Edition. This project packages
everything needed to **run Horizon's Minecraft 26.3 on macOS Intel** — no Microsoft account, offline /
cracked style — using the Minecraft files a TLauncher install already has.

It is not a launcher. It does not contain or reimplement TLauncher's code, ads, telemetry or auth
bypass. It only reuses the *Minecraft files*.

## Legal / disclaimer

- **Horizon** is MIT licensed (upstream project).
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

## What a fresh contributor needs (summary)

To get a working setup from scratch:

1. **Horizon** (`nightly-2026-11-01-c9d474d`) + Java 25 runtime — for preparation.
2. **Prepared Horizon resources** — from step 2 above.
3. **Minecraft files** — via `fetch-minecraft-26.3.py`.
4. **`play.sh`** — to launch.

The Python file is only step 3. It's the Minecraft-files fetcher, not the whole setup.

---

*This is a fan-made, abandoned-in-progress snapshot. Not affiliated with or endorsed by Mojang, Microsoft.*
