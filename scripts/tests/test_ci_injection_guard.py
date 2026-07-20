"""
Forked from claudesec scanner/tests/test_ci_no_code_injection_regression.py @
5226f53 (2026-07-20). Self-contained.

Regression guard: no CWE-94 (OWASP A03:2021 - Injection) code-injection sites
where a bash variable is interpolated DIRECTLY into a `python3 -c "..."` /
`python -c "..."` program body, and no UNQUOTED heredoc feeding a
code-executing interpreter.

THE RISK
--------
`python3 -c "... $VAR ... "` splices the shell variable's *text* into the
Python source before it is parsed. If that value can ever contain a quote,
backslash, or other Python-meaningful character, the interpolation breaks out
of its intended literal and executes as arbitrary Python - a classic CWE-94
code-injection bug (OWASP A03:2021: https://owasp.org/Top10/A03_2021-Injection/).
The fix is to pass the value through the process ENVIRONMENT -
`VAR="$value" python3 -c "..."` and `os.environ['VAR']` inside the program -
so the `-c` argument text is a constant with no `$` in it and the value can
never be re-parsed as Python source. This exact fix was applied to
`scripts/generate_svg_with_ai.sh` (5 sites) in the PR pairing with this guard.

WHAT THIS GUARD CHECKS
-----------------------
For every `*.sh` file in the repo (including `scripts/**` and `build.sh`), it
locates every `python3 -c "..."` / `python -c "..."` invocation whose `-c`
argument is DOUBLE-quoted, captures the program text up to the matching
(unescaped) closing double quote - programs commonly span multiple lines, so
the file is scanned as one joined text, not line-by-line - and flags the site
if that captured body contains ANY unescaped `$`. Whole-line `#` comments are
stripped first so a `$VAR` surviving only in a comment cannot trip the guard.

Detection rule: "any unescaped `$`"
-------------------------------------
Inside a bash double-quoted string, an unescaped `$` ALWAYS begins an
expansion - there is no double-quoted context where a bare `$` is inert. That
covers not just the named/braced/command-substitution forms (`$NAME`,
`${...}`, `$(...)`) but every positional and special parameter too: `$1`..`$9`,
`$0`, `$@`, `$*`, `$#`, `$?`, `$$`, `$!`, `$-`. A single "any unescaped `$`"
rule (`has_unescaped_dollar`) subsumes all of these in one check. A `\\$`
(backslash-escaped literal dollar) is correctly excluded.

Regression-pin semantics
-------------------------
The computed violation set (`"relpath:construct"`, one entry per offending
site) must EQUAL the baseline `KNOWN_INJECTION_SITES`. After the paired fix
PR, that baseline is the empty `set()` - i.e. this guard asserts NO
interpolated `python3 -c` double-quoted program remains in the repo. A NEW
site fails the guard immediately; shrinking the baseline without fixing the
site would also fail (keeps the allowlist honest). Adding an entry back to
`KNOWN_INJECTION_SITES` must be accompanied by a one-line justification
comment.

WHAT THIS GUARD ALSO CHECKS (unquoted heredoc into an interpreter)
--------------------------------------------------------------------
Beyond the `-c "..."` form above, this guard ALSO covers the structurally
identical CWE-94 risk of an UNQUOTED heredoc whose body is fed as the stdin
PROGRAM of a code-executing interpreter: `python3 <<EOF` / `bash <<EOF` /
`sh <<EOF` / `awk <<EOF` / `perl <<EOF` / `node <<EOF` / `ruby <<EOF`
(interpreter allowlist matched on the BASENAME of the command word - a
`/usr/bin/python3`-style full path also matches). A bare (unquoted) heredoc
delimiter (`<<EOF`, `<<-EOF`) does NOT disable expansion, so any unescaped `$`
in the body is interpolated by bash into the interpreter's source before it
runs. A QUOTED delimiter (`<<'EOF'` / `<<"EOF"`) is SAFE and not flagged. A
heredoc feeding a NON-interpreter command (`cat <<EOF`, `kubectl apply -f -
<<EOF`, `gh api --input - <<EOF`) is NEVER flagged even if its body contains
`$`, because that body is DATA, not code the shell hands to an interpreter.

Detection is conservative / what's OUT OF SCOPE
------------------------------------------------
This guard covers two construct families and is NOT a full injection
scanner:
  * `python3 -c '...'` (SINGLE-quoted `-c` argument) is SAFE and NOT flagged.
  * Values passed as `argv`, `stdin`, or the environment are the SAFE
    patterns this guard's fix moves callers toward, and are never flagged.
  * `awk -v var=... '...'` and any interpreter invocation not covered by the
    `-c "..."` form or the unquoted-heredoc form above are OUT OF SCOPE.
  * A `-c` argument built from adjacent CONCATENATED bash segments is
    PARTIALLY covered on a best-effort basis by `find_concatenated_c_bodies`.

Scan targets in this repo
--------------------------
Every `*.sh` file repo-wide (this naturally includes `scripts/**`, top-level
`build.sh`, and `.claude/hooks/*.sh`), every `.github/workflows/*.yml` /
`*.yaml` (scanned as raw text so a `run:` block's embedded shell is covered
by the same regexes), and a repo-root `Makefile` if one exists.

stdlib-only (no PyYAML). Self-contained: no import of any tech-blog product
code and no shared `_ci_guard_util` helper module - `strip_comment_lines` and
`has_unescaped_dollar` are inlined below. No network, no subprocess. Runs
under pytest (the CI runner) and `python3 -m unittest`.
"""

import re
import unittest
from pathlib import Path

# scripts/tests/this_file -> parents[0]=scripts/tests, [1]=scripts,
# [2]=repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Matches a whole-line `#` comment (leading whitespace then `#` to end of
# line) so a `$VAR` mentioned only in a comment cannot trip the guard.
_COMMENT_LINE_RE = re.compile(r"^\s*#.*$")


def strip_comment_lines(text: str) -> str:
    """Return `text` with every whole-line `#` comment blanked out (replaced
    by an empty line, so line numbers / DOTALL spans are unaffected)."""
    return "\n".join(
        "" if _COMMENT_LINE_RE.match(line) else line for line in text.splitlines()
    )


# Matches a `python3 -c "..."` / `python -c "..."` invocation whose `-c`
# argument is DOUBLE-quoted, capturing the program text up to the matching
# unescaped closing `"`. re.DOTALL so the body can span multiple lines.
_PYC_RE = re.compile(r'python3?\s+-c\s+"((?:\\.|[^"\\])*)"', re.DOTALL)

# The ACTUAL violation condition: any `$` in the captured body that is NOT
# immediately preceded by a backslash.
_UNESCAPED_DOLLAR_RE = re.compile(r"(?<!\\)\$")

# Recognizable expansion TOKEN shapes, used only to render a readable
# `relpath:construct` string in the violation report - NOT the detection
# condition (that is `has_unescaped_dollar`, below).
_DOLLAR_TOKEN_RE = re.compile(
    r"(?<!\\)\$(?:\{[^}]*\}|\([^)]*\)|[A-Za-z_][A-Za-z0-9_]*|[0-9@*#?$!-])"
)

# Regression baseline. MUST be empty after the paired fix PR - a non-empty
# entry here means a real CWE-94 site was found and deliberately deferred
# (each entry must carry a justification comment; none currently do because
# none should exist).
KNOWN_INJECTION_SITES: set = set()


def find_double_quoted_c_bodies(text: str) -> list:
    """The captured program-body text of every double-quoted `python3 -c "..."`
    / `python -c "..."` site in `text`, in document order."""
    return _PYC_RE.findall(text)


def has_unescaped_dollar(body: str) -> bool:
    """True if `body` contains ANY unescaped `$` - the actual violation
    condition."""
    return bool(_UNESCAPED_DOLLAR_RE.search(body))


def violating_constructs(body: str) -> list:
    """The recognizable `$`-expansion TOKENS found in one captured `-c`
    program body - used only to render a human-readable `relpath:construct`
    report string."""
    return _DOLLAR_TOKEN_RE.findall(body)


# Safe shell-terminator characters: if a `-c` argument's closing `"` is
# immediately followed by one of these, the shell word/command genuinely ends
# there. Anything else glued on with no separating whitespace is bash
# CONCATENATING more text onto the same word.
_SAFE_TERMINATOR_CHARS = set(" \t\n|&;)<>`")


def _scan_quoted_segment(text: str, pos: int):
    """`text[pos]` must be an opening `"`. Returns `(body, end_pos)` where
    `body` is the escaped-aware content up to the matching unescaped closing
    `"`, and `end_pos` is the index just past that closing quote (or
    `len(text)` if the quote is unterminated)."""
    i = pos + 1
    n = len(text)
    buf = []
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            buf.append(text[i : i + 2])
            i += 2
            continue
        if c == '"':
            return "".join(buf), i + 1
        buf.append(c)
        i += 1
    return "".join(buf), i


def find_concatenated_c_bodies(text: str) -> list:
    """Concatenation-aware capture of `python3 -c "..."` argument bodies
    (best-effort - see module docstring). Identical to
    `find_double_quoted_c_bodies` when the `-c` argument is a single
    double-quoted segment; when the segment's closing `"` is immediately
    followed by a non-terminator character, keeps consuming directly-adjacent
    double-quoted segments and concatenates their bodies before returning."""
    results = []
    n = len(text)
    for m in _PYC_RE.finditer(text):
        bodies = [m.group(1)]
        pos = m.end()
        while pos < n and text[pos] not in _SAFE_TERMINATOR_CHARS:
            if text[pos] == '"':
                seg_body, pos = _scan_quoted_segment(text, pos)
                bodies.append(seg_body)
            else:
                start = pos
                while (
                    pos < n
                    and text[pos] not in _SAFE_TERMINATOR_CHARS
                    and text[pos] != '"'
                ):
                    pos += 1
                if pos == start:  # defensive: never spin without progress
                    break
        results.append("".join(bodies))
    return results


# Matches a heredoc OPENER: `<<DELIM`, `<<-DELIM`, `<<'DELIM'`, `<<"DELIM"`.
# Group 1 = the optional `-` (leading-tab-stripping form). Groups 2/3 = the
# delimiter when single-/double-quoted (SAFE - expansion disabled). Group 4 =
# the delimiter when UNQUOTED (expansion active - the risk this guard checks).
_HEREDOC_OPEN_RE = re.compile(
    r"<<(-?)\s*(?:'([A-Za-z_][A-Za-z0-9_]*)'|\"([A-Za-z_][A-Za-z0-9_]*)\"|([A-Za-z_][A-Za-z0-9_]*))"
)

# Interpreter allowlist for the heredoc check: commands that EXECUTE their
# stdin as code. Matched on the basename of the leading command word.
_HEREDOC_INTERPRETER_RE = re.compile(r"^(?:.*/)?(python3?|sh|bash|awk|perl|node|ruby)$")

# Assignment prefix (`VAR=`) on a command word, e.g. `pyout="$(python3 ...`
_LEADING_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _strip_leading_noise(s: str) -> str:
    """Strip leading whitespace, `VAR=` assignment prefixes, quote chars
    (`"`/`'`), subshell/group openers (`$(`, `(`, `{`), and a standalone `!`
    (negation) - repeatedly, in that priority order - so that a command word
    glued directly onto one of these with no whitespace still resolves to the
    real leading command."""
    while True:
        stripped = s.lstrip()
        if stripped != s:
            s = stripped
            continue
        m = _LEADING_ASSIGN_RE.match(s)
        if m:
            s = s[m.end() :]
            continue
        if s[:2] == "$(":
            s = s[2:]
            continue
        if s[:1] in ("(", "{", '"', "'"):
            s = s[1:]
            continue
        if s[:1] == "!" and (len(s) == 1 or s[1].isspace()):
            s = s[1:]
            continue
        break
    return s


def _heredoc_owner_word(lines: list, idx: int, match) -> str:
    """The leading command word of the logical (backslash-continuation-joined)
    command line that owns the heredoc opener `match` found on `lines[idx]`."""
    start = idx
    while start > 0 and lines[start - 1].endswith("\\"):
        start -= 1
    parts = [
        lines[k][:-1] if lines[k].endswith("\\") else lines[k]
        for k in range(start, idx)
    ]
    parts.append(lines[idx][: match.start()])
    joined = _strip_leading_noise(" ".join(parts).strip())
    return joined.split()[0] if joined else ""


def find_interpreter_heredoc_sites(text: str) -> list:
    """Every heredoc in `text` whose owning command is a code-executing
    INTERPRETER (see `_HEREDOC_INTERPRETER_RE`), quoted or unquoted. Returns a
    list of `(interpreter, quoted, body)` tuples in document order."""
    lines = text.splitlines()
    n = len(lines)
    sites = []
    i = 0
    while i < n:
        m = _HEREDOC_OPEN_RE.search(lines[i])
        if not m:
            i += 1
            continue
        dash = m.group(1) == "-"
        quoted = m.group(2) is not None or m.group(3) is not None
        delim = m.group(2) or m.group(3) or m.group(4)
        j = i + 1
        body_lines = []
        while j < n:
            candidate = lines[j].lstrip("\t") if dash else lines[j]
            if candidate == delim:
                break
            body_lines.append(lines[j])
            j += 1
        word = _heredoc_owner_word(lines, i, m)
        if _HEREDOC_INTERPRETER_RE.match(word):
            sites.append((word, quoted, "\n".join(body_lines)))
        i = j + 1
    return sites


def _production_files() -> list:
    """Every `*.sh` file in the repo (repo-wide - covers `scripts/**`,
    top-level `build.sh`, and `.claude/hooks/*.sh`), every
    `.github/workflows/*.yml` / `*.yaml`, plus a repo-root `Makefile` if one
    exists."""
    files = sorted(
        p
        for p in REPO_ROOT.rglob("*.sh")
        if ".git" not in p.parts and "node_modules" not in p.parts
    )
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if workflows_dir.is_dir():
        files += sorted(workflows_dir.glob("*.yml"))
        files += sorted(workflows_dir.glob("*.yaml"))
    makefile = REPO_ROOT / "Makefile"
    if makefile.is_file():
        files.append(makefile)
    return files


def compute_violations(files) -> tuple:
    """Returns (violations, total_sites) - `violations` is the union of the
    `"relpath:construct"` (`python3 -c` sites, concatenation-aware) and
    `"relpath:heredoc:<interpreter>:construct"` (unquoted interpreter heredoc
    sites) violation sets; `total_sites` is the count of ALL double-quoted
    `python3 -c` sites scanned (violating or not), for the non-vacuity check."""
    violations = set()
    total_sites = 0
    for f in files:
        text = strip_comment_lines(Path(f).read_text(encoding="utf-8"))
        for body in find_concatenated_c_bodies(text):
            total_sites += 1
            if has_unescaped_dollar(body):
                rel = str(Path(f).resolve().relative_to(REPO_ROOT))
                tokens = violating_constructs(body)
                construct = ",".join(sorted(set(tokens))) if tokens else "$<unrecognized-shape>"
                violations.add(f"{rel}:{construct}")
        for interpreter, quoted, body in find_interpreter_heredoc_sites(text):
            if quoted:
                continue  # quoted delimiter disables expansion - SAFE
            if has_unescaped_dollar(body):
                rel = str(Path(f).resolve().relative_to(REPO_ROOT))
                tokens = violating_constructs(body)
                construct = ",".join(sorted(set(tokens))) if tokens else "$<unrecognized-shape>"
                violations.add(f"{rel}:heredoc:{interpreter}:{construct}")
    return violations, total_sites


class TestNoCodeInjectionRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = _production_files()

    def test_scan_set_nonempty(self):
        # If no *.sh files were found, the path assumptions broke - fail
        # loudly rather than vacuously passing the injection scan below.
        self.assertTrue(
            self.files,
            "No *.sh files found to scan - check the repo-wide rglob('*.sh') "
            "assumptions in _production_files().",
        )

    def test_parsed_non_trivial_number_of_sites(self):
        # Canary: if the `-c "..."` regex/paths broke, this would silently
        # find zero sites and the assertion below would vacuously pass.
        _, total_sites = compute_violations(self.files)
        self.assertGreater(
            total_sites, 3,
            "Parsed suspiciously few `python3 -c \"...\"` sites across the "
            "repo - the detection regex or file paths likely broke.",
        )

    def test_no_new_injection_site(self):
        violations, _ = compute_violations(self.files)
        new_violations = violations - KNOWN_INJECTION_SITES
        self.assertEqual(
            new_violations, set(),
            "NEW CWE-94 code-injection site(s) - a bash variable is "
            "interpolated directly into a `python3 -c \"...\"` program body "
            f"(OWASP A03:2021): {sorted(new_violations)}. Fix by passing the "
            "value through the environment (`VAR=\"$val\" python3 -c \"...\"` "
            "+ `os.environ['VAR']` inside the program) instead of splicing "
            "`$VAR`/`${...}`/`$(...)` into the program text.",
        )

    def test_no_stale_allowlist_entry(self):
        violations, _ = compute_violations(self.files)
        stale = KNOWN_INJECTION_SITES - violations
        self.assertEqual(
            stale, set(),
            f"KNOWN_INJECTION_SITES lists site(s) that are no longer "
            f"violations: {sorted(stale)} (fixed, or file removed/changed). "
            "Drop them from KNOWN_INJECTION_SITES so the baseline stays "
            "honest.",
        )


class TestInjectionDetectorMutation(unittest.TestCase):
    """Non-vacuity: the detector must FIRE on the unsafe interpolated form and
    stay QUIET on the safe single-quoted / argv / stdin / env-var forms."""

    def test_fires_on_dollar_var(self):
        body = "\n".join(["import json, os", "print(open('$OUTPUT_DIR/f.json'))"])
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: a bare `$VAR` interpolation was not detected.",
        )

    def test_fires_on_braced_var(self):
        body = "print('${CONTEXT}')"
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: a `${VAR}` interpolation was not detected.",
        )

    def test_fires_on_command_substitution(self):
        body = "print('$(date)')"
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: a `$(...)` command substitution was not "
            "detected.",
        )

    def test_fires_on_positional_param(self):
        body = "print('$1')"
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: positional parameter `$1` was not detected.",
        )

    def test_fires_on_special_param_at(self):
        body = "print('$@')"
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: special parameter `$@` was not detected.",
        )

    def test_quiet_on_escaped_dollar(self):
        # A backslash-escaped `\$` is a LITERAL dollar sign - bash does not
        # expand it inside the double-quoted -c argument, so it must not be
        # flagged.
        body = "print('\\$5.00')"
        self.assertFalse(
            has_unescaped_dollar(body),
            "False positive: an escaped `\\$` (literal dollar) was flagged "
            "as an expansion.",
        )

    def test_quiet_on_env_var_read(self):
        # The documented-safe fix: no `$` in the body at all.
        body = "\n".join(["import json, os", "print(open(os.environ['OCSF_FILE']))"])
        self.assertFalse(
            has_unescaped_dollar(body),
            "False positive: a body reading os.environ (the safe fix) was "
            "flagged.",
        )

    def test_quiet_on_single_quoted_c_argument(self):
        # A single-quoted -c argument must not even be captured as a site -
        # bash never expands $ inside single quotes.
        text = "python3 -c 'import os; print(os.environ[\"X\"])' 2>/dev/null"
        self.assertEqual(
            find_double_quoted_c_bodies(text), [],
            "False positive: a single-quoted `-c` argument was captured as "
            "a double-quoted site.",
        )

    def test_multiline_double_quoted_body_captured(self):
        # Programs typically span multiple lines between the opening
        # `-c "` and the closing `"` - the DOTALL capture must span them.
        text = 'python3 -c "\nimport os\nprint(os.environ[\'X\'])\n" 2>/dev/null'
        bodies = find_double_quoted_c_bodies(text)
        self.assertEqual(len(bodies), 1)
        self.assertIn("import os", bodies[0])

    def test_comment_only_reference_does_not_flag(self):
        # A `$VAR` mentioned only in a whole-line `#` comment (stripped
        # before scanning) must not be captured as part of a program body.
        text = "\n".join(
            [
                '# see $OUTPUT_DIR for context, not interpolated below',
                'python3 -c "import os; print(os.environ[\'OCSF_FILE\'])"',
            ]
        )
        stripped = strip_comment_lines(text)
        bodies = find_double_quoted_c_bodies(stripped)
        self.assertEqual(len(bodies), 1)
        self.assertFalse(has_unescaped_dollar(bodies[0]))

    # -- Blind spot #1: unquoted heredoc feeding an interpreter -----------

    def test_heredoc_fires_on_unquoted_python(self):
        text = 'python3 <<EOF\nprint("$HOME")\nEOF\n'
        sites = find_interpreter_heredoc_sites(text)
        self.assertEqual(len(sites), 1)
        interpreter, quoted, body = sites[0]
        self.assertEqual(interpreter, "python3")
        self.assertFalse(quoted)
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: an unquoted `python3 <<EOF` heredoc "
            "interpolating `$HOME` was not detected.",
        )

    def test_heredoc_fires_on_unquoted_bash(self):
        text = "bash <<EOF\nrm $TARGET\nEOF\n"
        sites = find_interpreter_heredoc_sites(text)
        self.assertEqual(len(sites), 1)
        interpreter, quoted, body = sites[0]
        self.assertEqual(interpreter, "bash")
        self.assertFalse(quoted)
        self.assertTrue(
            has_unescaped_dollar(body),
            "Mutation FAILED: an unquoted `bash <<EOF` heredoc interpolating "
            "`$TARGET` was not detected.",
        )

    def test_heredoc_quiet_on_quoted_delimiter(self):
        # `<<'EOF'` disables ALL expansion in the body - SAFE.
        text = "python3 <<'EOF'\nprint(\"$HOME\")\nEOF\n"
        sites = find_interpreter_heredoc_sites(text)
        self.assertEqual(len(sites), 1)
        _, quoted, _ = sites[0]
        self.assertTrue(
            quoted,
            "False positive risk: `<<'EOF'` (quoted delimiter) was not "
            "recognized as quoted.",
        )

    def test_heredoc_quiet_on_data_into_file(self):
        # `cat <<EOF > out.txt` - `cat` is not an interpreter; the heredoc is
        # DATA written to a file, not code the shell executes.
        text = "cat <<EOF > out.txt\n$HOME\nEOF\n"
        sites = find_interpreter_heredoc_sites(text)
        self.assertEqual(
            sites, [],
            "False positive: a `cat <<EOF > file` (data, non-interpreter) "
            "heredoc was flagged as interpreter-owned.",
        )

    def test_heredoc_quiet_on_non_interpreter_command(self):
        # `kubectl apply -f - <<EOF` - a Kubernetes manifest, not code.
        text = "kubectl apply -f - <<EOF\n  name: $x\nEOF\n"
        sites = find_interpreter_heredoc_sites(text)
        self.assertEqual(
            sites, [],
            "False positive: a `kubectl apply -f - <<EOF` (non-interpreter) "
            "heredoc was flagged as interpreter-owned.",
        )

    # -- Blind spot #2: quote-concatenation in a `-c` argument (best-effort) -

    def test_concatenation_fires_when_split_across_quoted_segments(self):
        text = 'python3 -c "a""$b"'
        bodies = find_concatenated_c_bodies(text)
        self.assertEqual(len(bodies), 1)
        self.assertTrue(
            has_unescaped_dollar(bodies[0]),
            "Mutation FAILED: a concatenated `-c \"a\"\"$b\"` argument did "
            "not have its second quoted segment's `$b` detected.",
        )

    def test_concatenation_quiet_on_normal_single_span(self):
        # Baseline: an ordinary single-quoted-span `-c` argument must produce
        # the SAME (safe) result as before - no false positive introduced by
        # the concatenation-aware capture.
        text = 'python3 -c "import os; print(os.environ[\'X\'])" 2>/dev/null'
        bodies = find_concatenated_c_bodies(text)
        self.assertEqual(len(bodies), 1)
        self.assertFalse(has_unescaped_dollar(bodies[0]))
        self.assertEqual(bodies, find_double_quoted_c_bodies(text))

    def test_real_repo_baseline_matches(self):
        # Full end-to-end check against the real production corpus, isolated
        # from the class-level test above so a fixture regression here can be
        # diagnosed independently.
        violations, _ = compute_violations(_production_files())
        self.assertEqual(
            violations, KNOWN_INJECTION_SITES,
            f"Live scan violations {sorted(violations)} do not match "
            f"KNOWN_INJECTION_SITES {sorted(KNOWN_INJECTION_SITES)}.",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
