"""Shared pieces of the extension review pipeline: OpenRouter access, the read-only workspace
that reviewers explore, and the review output format.

Standard library only. Nothing in this package ever runs code from an extension.
"""

import json
import os
import re
import time
import urllib.error
import urllib.request

OPENROUTER = "https://openrouter.ai/api/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
UPSTREAM_AGENTS_MD = "https://raw.githubusercontent.com/Slicer/ExtensionsIndex/main/AGENTS.md"

CRITERIA = ["safety", "environment", "packaging", "license", "soundness", "utility"]
RATINGS = ["ok", "minor", "concern", "blocking", "unknown"]  # rank = index, except unknown
SEVERITIES = ["info", "minor", "major", "blocking"]
OVERALL = ["no concerns", "minor issues", "needs fixes", "do not accept", "incomplete"]


class BudgetExhausted(Exception):
    """OpenRouter refused the request because the key's credit or limit is used up."""


class ModelError(Exception):
    pass


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def http_json(url, data=None, headers=None, timeout=300, method=None):
    body = json.dumps(data).encode() if data is not None else None
    h = {"User-Agent": "slicer-extensions-dashboard", "Accept": "application/json"}
    if body is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "null")


def http_text(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "slicer-extensions-dashboard"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# ----------------------------------------------------------------------------- OpenRouter

def openrouter_headers():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise ModelError("OPENROUTER_API_KEY is not set")
    return {"Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://github.com/pieper/extensions-dashboard",
            "X-Title": "Slicer extensions dashboard"}


def key_status():
    """Remaining credit on the key: {'limit': float|None, 'usage': float, 'remaining': float|None}."""
    for path in ("/key", "/auth/key"):
        try:
            d = http_json(OPENROUTER + path, headers=openrouter_headers(), timeout=30)["data"]
            return {"limit": d.get("limit"), "usage": d.get("usage", 0.0), "remaining": d.get("limit_remaining")}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
    return {"limit": None, "usage": None, "remaining": None}


def chat(model, messages, tools=None, tool_choice=None, max_tokens=6000, temperature=0.2):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
            "usage": {"include": True}}
    if tools:
        body["tools"] = tools
        body["tool_choice"] = tool_choice or "auto"
    last = None
    for attempt in range(5):
        try:
            r = http_json(OPENROUTER + "/chat/completions", body, headers=openrouter_headers(), timeout=600)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            if e.code == 402:
                raise BudgetExhausted(detail)
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(10 * (attempt + 1))
                last = f"HTTP {e.code}: {detail}"
                continue
            raise ModelError(f"HTTP {e.code}: {detail}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = str(e)
            time.sleep(10 * (attempt + 1))
            continue
        if r.get("error"):
            code = (r["error"] or {}).get("code")
            if code == 402:
                raise BudgetExhausted(str(r["error"]))
            last = str(r["error"])
            if attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise ModelError(last)
        if not r.get("choices"):
            last = "no choices in response"
            time.sleep(5)
            continue
        return r
    raise ModelError(f"giving up after retries: {last}")


# ----------------------------------------------------------------------------- read-only workspace

TEXT_EXTENSIONS = {".py", ".txt", ".md", ".rst", ".cmake", ".json", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".xml",
                   ".ui", ".cxx", ".cpp", ".cc", ".c", ".h", ".hxx", ".hpp", ".txx", ".sh", ".bat", ".ps1", ".js", ".ts",
                   ".html", ".css", ".qss", ".in", ".mrml", ".csv", ".sql", ".r", ".m", ".java", ".go", ".rs", ".ipynb"}


class Workspace:
    """An extracted extension repository that reviewers may list, read and search, nothing else."""

    MAX_READ_LINES = 400
    MAX_RESULT_CHARS = 14000

    def __init__(self, root):
        self.root = os.path.realpath(root)
        self.files = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = sorted(d for d in dirnames if d != ".git")
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                if os.path.islink(full):
                    continue
                self.files.append(os.path.relpath(full, self.root).replace(os.sep, "/"))
        self._cache = {}

    def resolve(self, path):
        path = (path or ".").strip().lstrip("/")
        full = os.path.realpath(os.path.join(self.root, path))
        if full != self.root and not full.startswith(self.root + os.sep):
            raise ValueError("path is outside the repository")
        return full

    def is_text(self, rel):
        ext = os.path.splitext(rel)[1].lower()
        name = os.path.basename(rel)
        if ext in TEXT_EXTENSIONS or name in ("CMakeLists.txt", "LICENSE", "LICENCE", "COPYING", "Makefile", "Dockerfile"):
            return True
        try:
            with open(self.resolve(rel), "rb") as f:
                return b"\0" not in f.read(4096)
        except OSError:
            return False

    def text(self, rel):
        if rel not in self._cache:
            full = self.resolve(rel)
            if os.path.getsize(full) > 2_000_000 or not self.is_text(rel):
                self._cache[rel] = None
            else:
                with open(full, "rb") as f:
                    self._cache[rel] = f.read().decode("utf-8", "replace")
        return self._cache[rel]

    # tools ----------------------------------------------------------------

    def list_files(self, path=".", max_depth=2):
        base = self.resolve(path)
        rel_base = os.path.relpath(base, self.root).replace(os.sep, "/")
        prefix = "" if rel_base == "." else rel_base + "/"
        depth = max(1, min(int(max_depth or 2), 6))
        out, seen_dirs = [], set()
        for f in self.files:
            if not f.startswith(prefix):
                continue
            parts = f[len(prefix):].split("/")
            if len(parts) > depth:
                d = prefix + "/".join(parts[:depth]) + "/"
                if d not in seen_dirs:
                    seen_dirs.add(d)
                    n = sum(1 for g in self.files if g.startswith(d))
                    out.append(f"{d}  ({n} files)")
                continue
            size = os.path.getsize(os.path.join(self.root, f))
            out.append(f"{f}  ({size} bytes{'' if self.is_text(f) else ', binary'})")
            if len(out) >= 400:
                out.append("... (truncated; list a subfolder)")
                break
        return "\n".join(out) or "(no files)"

    def read_file(self, path, start_line=1, end_line=None):
        rel = os.path.relpath(self.resolve(path), self.root).replace(os.sep, "/")
        if rel not in self.files:
            return f"No such file: {path}"
        t = self.text(rel)
        if t is None:
            return f"{rel} is binary or larger than 2 MB; it cannot be read as text."
        lines = t.splitlines()
        s = max(1, int(start_line or 1))
        e = min(len(lines), int(end_line) if end_line else s + self.MAX_READ_LINES - 1, s + self.MAX_READ_LINES - 1)
        body = "\n".join(f"{i:5d}  {lines[i - 1]}" for i in range(s, e + 1))
        more = f"\n[... file has {len(lines)} lines; read more with start_line={e + 1}]" if e < len(lines) else ""
        return clip(f"<file path=\"{rel}\" lines=\"{s}-{e}\">\n{body}\n</file>{more}", self.MAX_RESULT_CHARS)

    def search(self, pattern, path="."):
        try:
            rx = re.compile(pattern if len(pattern) <= 200 else re.escape(pattern[:200]), re.I)
        except re.error:
            rx = re.compile(re.escape(pattern), re.I)
        base = os.path.relpath(self.resolve(path), self.root).replace(os.sep, "/")
        prefix = "" if base == "." else base.rstrip("/") + "/"
        out = []
        for f in self.files:
            if prefix and not (f == base or f.startswith(prefix)):
                continue
            t = self.text(f)
            if t is None:
                continue
            for i, line in enumerate(t.splitlines(), 1):
                if len(line) < 3000 and rx.search(line):
                    out.append(f"{f}:{i}: {line.strip()[:240]}")
                    if len(out) >= 120:
                        return "\n".join(out) + "\n... (more matches; narrow the search)"
        return "\n".join(out) or "No matches."

    def dispatch(self, name, args):
        try:
            if name == "list_files":
                return self.list_files(args.get("path", "."), args.get("max_depth", 2))
            if name == "read_file":
                return self.read_file(args["path"], args.get("start_line", 1), args.get("end_line"))
            if name == "search":
                return self.search(args["pattern"], args.get("path", "."))
        except (KeyError, ValueError, TypeError, OSError) as e:
            return f"Tool error: {e}"
        return f"Unknown tool {name}"


def clip(s, n):
    return s if len(s) <= n else s[:n] + f"\n[... truncated {len(s) - n} characters]"


# ----------------------------------------------------------------------------- review format

def rating_schema():
    return {"type": "object", "properties": {
        "rating": {"type": "string", "enum": RATINGS},
        "rationale": {"type": "string", "description": "One to three sentences citing what you inspected."}},
        "required": ["rating", "rationale"]}


REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "purpose": {"type": "string", "description": "What the extension does and for whom, in two sentences."},
        "summary": {"type": "string", "description": "Your overall assessment in at most 120 words."},
        "overall": {"type": "string", "enum": OVERALL},
        "ratings": {"type": "object", "properties": {c: rating_schema() for c in CRITERIA}, "required": CRITERIA},
        "findings": {"type": "array", "items": {"type": "object", "properties": {
            "category": {"type": "string", "enum": CRITERIA},
            "severity": {"type": "string", "enum": SEVERITIES},
            "title": {"type": "string", "description": "One line."},
            "file": {"type": "string", "description": "Path relative to the repository root, or empty."},
            "line_start": {"type": "integer"},
            "line_end": {"type": "integer"},
            "evidence": {"type": "string", "description": "Exact text copied from the file (one to five lines), or empty."},
            "explanation": {"type": "string", "description": "Why it matters: the concrete path to harm or failure."},
            "suggestion": {"type": "string"},
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]}},
            "required": ["category", "severity", "title", "explanation", "confidence"]}},
        "not_checked": {"type": "array", "items": {"type": "string"},
                        "description": "What you could not inspect or verify."},
        "questions_for_author": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["purpose", "summary", "overall", "ratings", "findings", "not_checked"],
}


def _s(v, n):
    return re.sub(r"\s+\Z", "", str(v if v is not None else ""))[:n]


def normalize_review(r):
    """Coerce a reviewer's submission into the expected shape, dropping anything unexpected."""
    if not isinstance(r, dict):
        raise ValueError("review is not an object")
    out = {"purpose": _s(r.get("purpose"), 600), "summary": _s(r.get("summary"), 1500),
           "overall": r.get("overall") if r.get("overall") in OVERALL else "incomplete", "ratings": {}, "findings": [],
           "not_checked": [_s(x, 300) for x in (r.get("not_checked") or [])[:15] if x],
           "questions_for_author": [_s(x, 400) for x in (r.get("questions_for_author") or [])[:10] if x]}
    ratings = r.get("ratings") if isinstance(r.get("ratings"), dict) else {}
    for c in CRITERIA:
        v = ratings.get(c) if isinstance(ratings.get(c), dict) else {}
        out["ratings"][c] = {"rating": v.get("rating") if v.get("rating") in RATINGS else "unknown",
                             "rationale": _s(v.get("rationale"), 800)}
    for f in (r.get("findings") or [])[:40]:
        if not isinstance(f, dict) or not f.get("title"):
            continue

        def num(x):
            try:
                return int(x) if x not in (None, "") else None
            except (TypeError, ValueError):
                return None
        out["findings"].append({
            "category": f.get("category") if f.get("category") in CRITERIA else "soundness",
            "severity": f.get("severity") if f.get("severity") in SEVERITIES else "minor",
            "title": _s(f.get("title"), 200), "file": _s(f.get("file"), 300).lstrip("./") if f.get("file") else "",
            "line_start": num(f.get("line_start")), "line_end": num(f.get("line_end")),
            "evidence": _s(f.get("evidence"), 1200), "explanation": _s(f.get("explanation"), 1500),
            "suggestion": _s(f.get("suggestion"), 800),
            "confidence": f.get("confidence") if f.get("confidence") in ("high", "medium", "low") else "medium"})
    return out


def parse_json_text(text):
    """Pull the first JSON object out of a model's plain-text answer."""
    if not text:
        return None
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    candidate = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    try:
        return json.loads(candidate)
    except (json.JSONDecodeError, ValueError):
        return None
