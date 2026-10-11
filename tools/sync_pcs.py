#!/usr/bin/env python3
"""Keep the PCs that work on this repository in step with GitHub.

Run by the Claude Code hooks in .claude/settings.json, or by hand:

    python tools/sync_pcs.py start   # bring main up to date before working
    python tools/sync_pcs.py push    # after a commit: rebase on GitHub, push
    python tools/sync_pcs.py check   # at the end: anything not on GitHub?

Each prints a JSON object for the hook (additionalContext for Claude,
systemMessage for the person). It never discards work: local changes are
stashed around the rebase, and a conflict stops the rebase and says so.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "main"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def counts() -> tuple[int, int]:
    """(commits only here, commits only on GitHub)."""
    out = git("rev-list", "--left-right", "--count", f"{BRANCH}...origin/{BRANCH}").stdout.split()
    return (int(out[0]), int(out[1])) if len(out) == 2 else (0, 0)


def dirty() -> list[str]:
    return [line for line in git("status", "--porcelain").stdout.splitlines() if line.strip()]


def rebase() -> str | None:
    """Rebase main on GitHub's; an error message, or None."""
    result = git("pull", "--rebase", "--autostash", "origin", BRANCH)
    if result.returncode != 0:
        git("rebase", "--abort")
        return (result.stdout + result.stderr).strip()[-800:]
    return None


def emit(event: str, context: str, message: str | None = None) -> None:
    out: dict = {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}}
    if message:
        out["systemMessage"] = message
    print(json.dumps(out, ensure_ascii=False))


def start() -> None:
    if git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() != BRANCH:
        emit("SessionStart", f"sync_pcs: not on {BRANCH}; nothing synced.")
        return
    if git("fetch", "-q", "origin").returncode != 0:
        emit("SessionStart", "sync_pcs: GitHub unreachable; working on the local copy.",
             "Sincronização: sem acesso ao GitHub, trabalhando na cópia local.")
        return
    ahead, behind = counts()
    error = rebase() if behind else None
    if error:
        emit("SessionStart",
             f"sync_pcs: main is {behind} commit(s) behind GitHub and the rebase stopped on a "
             f"conflict (aborted, nothing lost). Resolve it with the user before working.\n{error}",
             "Sincronização: conflito ao trazer os commits do outro PC; resolva antes de continuar.")
        return
    new = git("log", "--oneline", f"-{behind}", f"origin/{BRANCH}").stdout.strip() if behind else ""
    ahead, _ = counts()
    lines = [f"sync_pcs: main is up to date with GitHub ({behind} new commit(s) pulled)."]
    if new:
        lines.append("Pulled from the other PC:\n" + new)
    if ahead:
        lines.append(f"{ahead} local commit(s) not yet on GitHub: push them (python tools/sync_pcs.py push).")
    emit("SessionStart", "\n".join(lines),
         f"Sincronização: {behind} commit(s) do outro PC trazido(s)." if behind else None)


def push() -> None:
    # From the hook, stdin holds the tool call: act only after a git commit.
    if not sys.stdin.isatty():
        try:
            command = json.loads(sys.stdin.read() or "{}").get("tool_input", {}).get("command", "")
        except ValueError:
            command = ""
        if command and "git commit" not in command:
            return
    if git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() != BRANCH:
        return
    git("fetch", "-q", "origin")
    ahead, behind = counts()
    if not ahead:
        return
    error = rebase() if behind else None
    if error:
        emit("PostToolUse",
             "sync_pcs: the other PC pushed meanwhile and the rebase conflicts (aborted, the commit "
             f"is safe locally). Resolve with the user, then push.\n{error}",
             "Sincronização: conflito com commits do outro PC; o commit está salvo só aqui.")
        return
    result = git("push", "-q", "origin", BRANCH)
    for _ in range(3):
        # The other PC pushed in the same moment: rebase on it and try again.
        if result.returncode == 0 or rebase() is not None:
            break
        behind += 1
        result = git("push", "-q", "origin", BRANCH)
    if result.returncode != 0:
        emit("PostToolUse", "sync_pcs: push failed; the commit is only local.\n" + result.stderr[-500:],
             "Sincronização: push falhou; o commit está só neste PC.")
        return
    note = f" after rebasing on {behind} commit(s) from the other PC" if behind else ""
    emit("PostToolUse", f"sync_pcs: pushed {ahead} commit(s) to GitHub{note}.")


def check() -> None:
    git("fetch", "-q", "origin")
    ahead, _ = counts()
    changes = dirty()
    if not ahead and not changes:
        return
    parts = []
    if ahead:
        parts.append(f"{ahead} commit(s) não enviado(s) ao GitHub")
    if changes:
        parts.append(f"{len(changes)} arquivo(s) alterado(s) sem commit")
    print(json.dumps({"systemMessage": "Sincronização: " + " e ".join(parts)
                      + ". O outro PC não vai ver isso até o commit e o push."}, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # the hook reads UTF-8, not the console's code page
    {"start": start, "push": push, "check": check}[sys.argv[1] if len(sys.argv) > 1 else "check"]()
