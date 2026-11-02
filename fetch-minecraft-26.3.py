#!/usr/bin/env python3
"""Fill a TLauncher-style Minecraft folder with the exact 26.3 files Horizon pins.

Horizon (the Rust client) does not download Minecraft. It prepares its resources
from a normal Minecraft install: version json + client jar + libraries + assets.
TLauncher keeps exactly that layout under its game folder, so this script rebuilds
the bytes TLauncher would have downloaded, straight from Mojang, using the sha1s
in the installed Horizon version's research-lock.json.

Usage: fetch-minecraft-26.3.py <minecraft-dir> [--version-dir <horizon-version-dir>]

Existing files with the right sha1 are left alone, so it is safe to re-run and it
turns a half-installed folder into a complete one.
"""

import hashlib
import json
import os
import subprocess
import sys
import concurrent.futures

META = "https://piston-meta.mojang.com"
OBJECTS = "https://piston-data.mojang.com/v1/objects"
RESOURCES = "https://resources.download.minecraft.net"


def sha1_of(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fetch(url, path, sha=None, size=None):
    """Download url to path unless a file with the same sha1 is already there."""
    if os.path.exists(path):
        if sha is None:
            return
        if os.path.getsize(path) == (size or os.path.getsize(path)) and sha1_of(path) == sha:
            return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".part"
    last = None
    for _ in range(4):
        r = subprocess.run(["curl", "-sL", "--fail", "--retry", "2", "--max-time", "300",
                            "-o", tmp, url])
        if r.returncode != 0:
            last = f"curl exit {r.returncode}"
            continue
        if sha and sha1_of(tmp) != sha:
            last = "sha1 mismatch"
            continue
        os.replace(tmp, path)
        return
    raise SystemExit(f"could not download {url}: {last}")


def find_horizon_version(explicit):
    if explicit:
        return explicit
    beside = os.path.join(os.path.dirname(os.path.abspath(__file__)), "home")
    home = (os.environ.get("HORIZON_LAUNCHER_HOME")
            or (beside if os.path.isdir(os.path.join(beside, "versions")) else None)
            or os.path.expanduser("~/Library/Application Support/horizon-launcher"))
    settings = os.path.join(home, "settings.json")
    versions = os.path.join(home, "versions")
    if os.path.exists(settings) and os.path.isdir(versions):
        try:
            selected = json.load(open(settings)).get("selected")
        except Exception:
            selected = None
        if selected and os.path.isdir(os.path.join(versions, selected)):
            return os.path.join(versions, selected)
        installed = sorted(d for d in os.listdir(versions) if os.path.isdir(os.path.join(versions, d)))
        if installed:
            return os.path.join(versions, installed[-1])
    raise SystemExit("pass --version-dir: the Horizon version folder with research-lock.json")


def main():
    args = sys.argv[1:]
    explicit = None
    if "--version-dir" in args:
        i = args.index("--version-dir")
        explicit = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        raise SystemExit("usage: fetch-minecraft-26.3.py <minecraft-dir> [--version-dir <horizon-version-dir>]")
    mc = os.path.abspath(os.path.expanduser(args[0]))
    version_dir = find_horizon_version(explicit)

    lock = json.load(open(os.path.join(version_dir, "research-lock.json")))["minecraft"]
    version = lock["version"]
    manifest_sha1 = lock["manifest_sha1"]
    client_sha1 = lock["client_sha1"]
    server_sha1 = lock["server_sha1"]

    print(f"Minecraft {version} into {mc}")
    print(f"pins from {version_dir}")

    version_path = os.path.join(mc, "versions", version)
    os.makedirs(version_path, exist_ok=True)

    manifest_path = os.path.join(version_path, f"{version}.json")
    fetch(f"{META}/v1/packages/{manifest_sha1}/{version}.json", manifest_path, manifest_sha1)
    manifest = json.load(open(manifest_path))

    jobs = []
    fetch(f"{OBJECTS}/{client_sha1}/client.jar",
          os.path.join(version_path, f"{version}.jar"), client_sha1)
    fetch(f"{OBJECTS}/{server_sha1}/server.jar",
          os.path.join(mc, f"server-{version}.jar"), server_sha1)

    index = manifest["assetIndex"]
    index_path = os.path.join(mc, "assets", "indexes", f"{index['id']}.json")
    fetch(f"{META}/v1/packages/{index['sha1']}/{index['id']}.json", index_path, index["sha1"])

    libraries = 0
    for lib in manifest.get("libraries", []):
        downloads = lib.get("downloads", {})
        artifact = downloads.get("artifact")
        if artifact:
            fetch(artifact["url"], os.path.join(mc, "libraries", artifact["path"]),
                  artifact.get("sha1"), artifact.get("size"))
            libraries += 1
        key = (lib.get("natives") or {}).get("osx")
        if key:
            key = key.replace("${arch}", "64")
            native = downloads.get("classifiers", {}).get(key)
            if native:
                fetch(native["url"], os.path.join(mc, "libraries", native["path"]),
                      native.get("sha1"), native.get("size"))
                libraries += 1

    index_json = json.load(open(index_path))
    objects = {}
    for obj in index_json["objects"].values():
        objects[obj["hash"]] = obj["size"]
    have = 0
    todo = []
    for h, size in objects.items():
        path = os.path.join(mc, "assets", "objects", h[:2], h)
        if os.path.exists(path) and os.path.getsize(path) == size:
            have += 1
        else:
            todo.append((h, size))

    print(f"{libraries} libraries, {len(objects)} asset objects ({have} already there, {len(todo)} to fetch)")

    done = 0
    def one(item):
        nonlocal done
        h, size = item
        fetch(f"{RESOURCES}/{h[:2]}/{h}", os.path.join(mc, "assets", "objects", h[:2], h), h, size)
        done += 1
        if done % 250 == 0:
            print(f"  {done}/{len(todo)} assets", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(one, todo))

    marker = os.path.join(mc, "tlauncher_profiles.json")
    if not os.path.exists(marker):
        with open(marker, "w") as f:
            json.dump({"profiles": {}}, f, indent=2)

    print(f"done: {mc}")


if __name__ == "__main__":
    main()
