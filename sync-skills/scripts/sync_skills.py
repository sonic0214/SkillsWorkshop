#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


IGNORE_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".factory",
    "__pycache__",
    "node_modules",
}

IGNORE_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}


@dataclass(frozen=True)
class SkillVersion:
    root: Path
    path: Path
    manifest: dict


def _codex_home() -> Path:
    env = os.environ.get("CODEX_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".codex"


def _config_path() -> Path:
    return _codex_home() / "skill-sync" / "config.json"


def _load_config() -> dict:
    cfg_path = _config_path()
    if not cfg_path.is_file():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to parse config: {cfg_path} ({e})")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_files(base: Path) -> Iterable[Path]:
    # Prefer os.walk for speed + ignore control.
    for root, dirnames, filenames in os.walk(base):
        root_path = Path(root)
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES and not d.startswith(".sync-")]
        for name in filenames:
            if name in IGNORE_FILE_NAMES:
                continue
            yield root_path / name


def _build_manifest(skill_dir: Path) -> dict:
    files: dict[str, dict] = {}
    latest_mtime = 0.0
    for f in _iter_files(skill_dir):
        try:
            st = f.stat()
        except FileNotFoundError:
            continue
        rel = f.relative_to(skill_dir).as_posix()
        latest_mtime = max(latest_mtime, st.st_mtime)
        files[rel] = {
            "sha256": _sha256_file(f),
            "size": st.st_size,
        }
    return {"files": files, "latest_mtime": latest_mtime}


def _is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def _list_skills(root: Path) -> dict[str, Path]:
    skills: dict[str, Path] = {}
    if not root.is_dir():
        return skills
    for child in root.iterdir():
        if child.name.startswith("."):
            continue
        if _is_skill_dir(child):
            skills[child.name] = child
    return skills


def _normalize_roots(roots: Iterable[str]) -> list[Path]:
    out: list[Path] = []
    for r in roots:
        p = Path(r).expanduser().resolve()
        if p not in out:
            out.append(p)
    return out


def _discover_factory_skills_dirs_from_cwd(cwd: Path) -> list[Path]:
    out: list[Path] = []
    for p in [cwd, *cwd.parents]:
        candidate = p / ".factory" / "skills"
        if candidate.is_dir() and candidate not in out:
            out.append(candidate)
    return out


def _discover_default_roots(cwd: Path) -> list[Path]:
    roots: list[Path] = []

    home_factory = Path.home() / ".factory" / "skills"
    roots.append(home_factory.resolve())

    roots.extend(_discover_factory_skills_dirs_from_cwd(cwd))

    claude_skills = Path.home() / ".claude" / "skills"
    roots.append(claude_skills.resolve())

    codex_skills = _codex_home() / "skills"
    roots.append(codex_skills.resolve())

    # De-dupe while preserving order.
    uniq: list[Path] = []
    for r in roots:
        if r not in uniq:
            uniq.append(r)
    return uniq


def _manifest_equal(a: dict, b: dict) -> bool:
    return a.get("files", {}) == b.get("files", {})


def _backup_dir() -> Path:
    base = _codex_home() / "skill-sync" / "backups"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _slug_path(p: Path) -> str:
    s = p.as_posix()
    s = s.replace(":", "")
    s = s.strip("/").replace("/", "__")
    return s or "root"


def _backup_skill_dir(dest_skill_dir: Path, root: Path, skill_name: str) -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = _backup_dir() / ts / _slug_path(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"{skill_name}.tar.gz"
    with tarfile.open(archive, mode="w:gz") as tf:
        tf.add(dest_skill_dir, arcname=skill_name)
    return archive


def _run_rsync(src_dir: Path, dest_dir: Path, dry_run: bool) -> None:
    # Copy *contents* of src_dir into dest_dir.
    cmd = [
        "rsync",
        "-a",
        "--checksum",
        "--delete",
        "--exclude",
        ".DS_Store",
        "--exclude",
        "__pycache__/",
        "--exclude",
        "node_modules/",
        "--exclude",
        ".git/",
    ]
    if dry_run:
        cmd.append("--dry-run")
    cmd.extend([f"{src_dir.as_posix().rstrip('/')}/", f"{dest_dir.as_posix().rstrip('/')}/"])

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"rsync failed ({res.returncode}): {' '.join(cmd)}\n{res.stderr.strip()}")


def _choose_source(versions: list[SkillVersion], prefer: str) -> SkillVersion:
    if prefer == "newest":
        return max(versions, key=lambda v: v.manifest.get("latest_mtime", 0.0))
    raise ValueError(f"Unsupported prefer mode: {prefer}")


def _print_root_summary(roots: list[Path], skills_by_root: dict[Path, dict[str, Path]], union: list[str]) -> None:
    print("\n== Roots ==")
    for r in roots:
        skills = skills_by_root.get(r, {})
        missing = [s for s in union if s not in skills]
        print(f"- {r} ({len(skills)}/{len(union)})")
        if missing:
            print(f"  missing: {', '.join(missing)}")


def _diff_hint(a: Path, b: Path) -> str:
    return f"diff -ru {shlex.quote(a.as_posix())} {shlex.quote(b.as_posix())}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Diff + sync skills across multiple skill roots.")
    ap.add_argument(
        "--roots",
        nargs="*",
        default=None,
        help="Explicit skill roots (directories containing <skill>/SKILL.md). If omitted, auto-discover.",
    )
    ap.add_argument("--apply", action="store_true", help="Apply sync (overwrites destinations).")
    ap.add_argument("--prefer", default=None, help="Conflict resolution: newest (default).")
    ap.add_argument(
        "--include-repo",
        action="store_true",
        help="Include <repo_root>/.factory/skills even if missing (created on --apply).",
    )
    ap.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to use with --include-repo (defaults to cwd).",
    )
    args = ap.parse_args()

    cfg = _load_config()
    prefer = args.prefer or cfg.get("prefer") or "newest"

    cwd = Path.cwd()
    if args.roots is not None and len(args.roots) > 0:
        roots = _normalize_roots(args.roots)
    else:
        cfg_roots = cfg.get("roots")
        if isinstance(cfg_roots, list) and cfg_roots:
            roots = _normalize_roots([str(x) for x in cfg_roots])
        else:
            roots = _discover_default_roots(cwd)

    if args.include_repo:
        repo_base = Path(args.repo_root).expanduser().resolve() if args.repo_root else cwd
        repo_skills = repo_base / ".factory" / "skills"
        roots = _normalize_roots([*roots, repo_skills])

    if args.apply:
        for r in roots:
            r.mkdir(parents=True, exist_ok=True)
    roots = [r for r in roots if r.is_dir()]
    if len(roots) < 2:
        print("Need at least 2 skill roots to sync.")
        for r in roots:
            print(f"- {r}")
        print("\nTip: use --roots or create config at:", _config_path())
        return 1

    skills_by_root: dict[Path, dict[str, Path]] = {r: _list_skills(r) for r in roots}
    union = sorted({name for m in skills_by_root.values() for name in m.keys()})
    if not union:
        print("No skills found under roots:")
        for r in roots:
            print(f"- {r}")
        return 1

    _print_root_summary(roots, skills_by_root, union)

    # Build manifests per (root, skill).
    versions_by_skill: dict[str, list[SkillVersion]] = {}
    for r in roots:
        for name, p in skills_by_root[r].items():
            versions_by_skill.setdefault(name, []).append(SkillVersion(root=r, path=p, manifest=_build_manifest(p)))

    changes: list[str] = []
    conflicts: list[str] = []
    diff_hints: dict[str, str] = {}

    for skill_name in union:
        versions = versions_by_skill.get(skill_name, [])
        if not versions:
            continue

        # Determine if there are differing versions.
        all_equal = True
        for i in range(1, len(versions)):
            if not _manifest_equal(versions[0].manifest, versions[i].manifest):
                all_equal = False
                break

        src = versions[0] if all_equal else _choose_source(versions, prefer)
        if not all_equal:
            conflicts.append(
                f"{skill_name}: conflict across {len(versions)} roots; selected source: {src.root}"
            )
            other = next((v for v in versions if v.root != src.root), None)
            if other:
                diff_hints[skill_name] = _diff_hint(src.path, other.path)

        for dest_root in roots:
            dest_dir = dest_root / skill_name
            if dest_root == src.root:
                continue
            dest_exists = _is_skill_dir(dest_dir)
            if dest_exists:
                dest_manifest = _build_manifest(dest_dir)
                if _manifest_equal(src.manifest, dest_manifest):
                    continue
                if args.apply:
                    archive = _backup_skill_dir(dest_dir, dest_root, skill_name)
                    changes.append(f"{skill_name}: backup {dest_root} -> {archive}")
            if args.apply:
                dest_dir.mkdir(parents=True, exist_ok=True)
            _run_rsync(src.path, dest_dir, dry_run=not args.apply)
            changes.append(f"{skill_name}: sync {src.root} -> {dest_root}")

    if conflicts:
        print("\n== Conflicts ==")
        for c in conflicts:
            print(f"- {c}")
        for skill_name, hint in sorted(diff_hints.items()):
            print(f"- {skill_name}: diff hint: {hint}")
    if changes:
        print("\n== Actions ==")
        for c in changes:
            print(f"- {c}")
    else:
        print("\nNo changes needed; all roots already match.")

    # Verify after apply.
    if args.apply:
        print("\n== Verify ==")
        re_skills_by_root = {r: _list_skills(r) for r in roots}
        re_union = sorted({name for m in re_skills_by_root.values() for name in m.keys()})
        ok = True
        for r in roots:
            missing = [s for s in re_union if s not in re_skills_by_root[r]]
            if missing:
                ok = False
                print(f"- FAIL {r}: missing {', '.join(missing)}")
        # Check per-skill equality.
        for skill_name in re_union:
            manifests: list[tuple[Path, dict]] = []
            for r in roots:
                p = r / skill_name
                if not _is_skill_dir(p):
                    continue
                manifests.append((r, _build_manifest(p)))
            if len(manifests) < 2:
                continue
            base_root, base_manifest = manifests[0]
            for r, m in manifests[1:]:
                if not _manifest_equal(base_manifest, m):
                    ok = False
                    print(f"- FAIL {skill_name}: differs between {base_root} and {r}")
                    print(f"  hint: {_diff_hint(base_root / skill_name, r / skill_name)}")
        if ok:
            print("- OK: all roots contain the same full set of skills with identical contents.")
            return 0
        return 2

    print("\nTip: re-run with --apply to sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
