#!/usr/bin/env python3
"""PreToolUse hard-deny guard (registered in ~/.config/devin/config.json).

Deterministic replacement for the former rules/auto-mode.md self-regulation
layer. Blocks only catastrophic or credential-compromising actions; softer
operations stay governed by permissions.ask in config.json.

Input:  stdin JSON {tool_name, tool_input, ...}
Output: {"decision": "block", "reason": ...} + exit 2 on match, else exit 0.
"""
import json
import re
import sys

BLOCK_DEVICES = r"/dev/(?:sd|nvme|vd|xvd|hd|disk|mmcblk|loop)"
CRED_PATHS = re.compile(
    r"(\.ssh/|\.aws/(credentials|config)\b|\.gnupg/|\.git/hooks/|(^|[/\s])\.env(\.|$|\s))"
)

# (pattern, reason) — matched against any shell-payload field.
CMD_RULES = [
    (r"--no-preserve-root", "rm --no-preserve-root"),
    (r":\s*\(\s*\)\s*\{", "fork bomb"),
    (r"\b(?:curl|wget)\b[^|;&]*\|\s*(?:sudo\s+)?(?:env\s+\w+=\S+\s+)*(?:ba|da|z|fi|k|c)?sh\b",
     "pipe remote content to shell"),
    (r"\bdd\b[^|;&]*\bof\s*=\s*" + BLOCK_DEVICES, "dd write to block device"),
    (r">\s*" + BLOCK_DEVICES, "redirect write to block device"),
    (r"\b(?:mkfs|wipefs|shred)\b[^|;&]*" + BLOCK_DEVICES, "filesystem destruction on device"),
    (r"\bmkfs\b", "mkfs"),
    (r"\bchmod\b[^|;&]*-[a-zA-Z]*R[a-zA-Z]*[^|;&]*\b(777|666|a\+rwx)\s+(?:/|~|\$HOME|\$\{HOME\})(?:\s|$|/)",
     "recursive permissive chmod on root/home"),
]

DANGEROUS_RM_TARGET = re.compile(
    r"(?:^|\s)(?:/|~|\$HOME|\$\{HOME\}|\.git|\.|\.\.|\*|/\*)\s*(?:$|\s)"
)


def check_exec(cmd: str) -> None:
    for pattern, reason in CMD_RULES:
        if re.search(pattern, cmd):
            block(reason)
    for m in re.finditer(r"\brm\s+([^|;&]+)", cmd):
        seg = m.group(1)
        if re.search(r"-{1,2}[\w=]*[rR]", seg) and DANGEROUS_RM_TARGET.search(seg):
            block("recursive rm on root/home/.git/wildcard target")
    for m in re.finditer(r"\bgit\s+push\b([^|;&]*)", cmd):
        seg = m.group(1)
        if re.search(r"--force(?:-with-lease)?|-f\b|--delete", seg) and re.search(
            r"\b(main|master|HEAD)\b", seg
        ):
            block("force-push or delete on main/master/HEAD")
        if re.search(r":(main|master)\b", seg):
            block("push-delete on main/master")
    for m in re.finditer(r"(?:>>?|tee\s+)\s*([^\s|;&]+)", cmd):
        if CRED_PATHS.search(m.group(1)):
            block("write to credential/env path")


def check_path(path: str) -> None:
    if CRED_PATHS.search(path):
        block("write to credential/env path")


def block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": f"deny-guard: {reason}"}))
    sys.exit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return  # unparseable input: let permissions.* decide
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    if tool in ("exec",):
        check_exec(str(ti.get("command", "")))
    elif tool == "write_to_process":
        check_exec(str(ti.get("text_input", "")))
        check_exec(str(ti.get("bytes_input", "")))
    elif tool in ("write", "edit", "apply_patch", "notebook_edit"):
        check_path(str(ti.get("file_path") or ti.get("notebook_path") or ""))


if __name__ == "__main__":
    main()
