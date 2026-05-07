# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]

SKIP_SUFFIXES = ('.snippet', '.snippet.md')
SKIP_DIR_PARTS = {'.git', '.github', '__pycache__', '.pytest_cache'}
REQUIRE_EVIDENCE_IN = {
    'concepts',
    'paradigms',
    'architecture',
    'categories',
    'design-space',
    'projects',
    'synthesis',
    'evaluation',
    'index',
    'meta',
    'starter-kit',
    'toolkit',
}
LINK_RE = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
CODE_PATH_RE = re.compile(r'`([^`\n]+)`')
KNOWN_PATH_ROOTS = {
    'AGENTS.md',
    'ARCHITECTURE.md',
    'SKILL.md',
    'START-HERE.md',
    'architecture',
    'categories',
    'cognitive-architecture',
    'concepts',
    'design-space',
    'evaluation',
    'guides',
    'index',
    'meta',
    'paradigms',
    'projects',
    'starter-kit',
    'synthesis',
    'toolkit',
}

EVIDENCE_RE = re.compile(
    r'(>\s*\*\*证据\*\*|>\s*\*\*Evidence Status\*\*|##\s*Evidence Status)'
)
# Matches the level after "— level" in an evidence status line
EVIDENCE_LEVEL_RE = re.compile(r'—\s*(\S+?)[\s.,]|—\s*(\S+)$')


def iter_markdown_files() -> Iterable[Path]:
    for path in ROOT.rglob('*.md'):
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        if path.name.endswith(SKIP_SUFFIXES):
            continue
        yield path


def relative_to_root(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def is_template(path: Path) -> bool:
    """Template files are exempt from validation."""
    rel = relative_to_root(path)
    if 'template' in path.name.lower():
        return True
    if any(part.lower() == 'templates' for part in rel.parts):
        return True
    return False


def needs_evidence_status(path: Path) -> bool:
    rel = relative_to_root(path)
    if is_template(path):
        return False
    if rel.name == 'SKILL.md' and len(rel.parts) == 1:
        return False
    if rel in {Path('ARCHITECTURE.md'), Path('AGENTS.md'), Path('ENHANCEMENT-NOTES.md')}:
        return True
    return bool(rel.parts) and rel.parts[0] in REQUIRE_EVIDENCE_IN


def _strip_code_blocks(lines: List[str]) -> List[str]:
    """Return lines with fenced code block content replaced by empty strings."""
    result = []
    in_code = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            result.append('')
            continue
        result.append('' if in_code else line)
    return result


def extract_evidence_level(line: str) -> str | None:
    """Extract the evidence level from a line like '> **Evidence Status** — synthesized.'"""
    m = EVIDENCE_LEVEL_RE.search(line)
    if m:
        level = (m.group(1) or m.group(2)).rstrip('.')
        return level
    return None


def check_evidence_status(path: Path) -> Tuple[List[str], str | None]:
    """Returns (errors, evidence_level_or_None)."""
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    errors: List[str] = []

    if not needs_evidence_status(path):
        return errors, None

    # Only check the first 10 lines, excluding code block content
    head = lines[:10]
    head_clean = _strip_code_blocks(head)

    found = False
    found_level = None
    for line in head_clean:
        if EVIDENCE_RE.search(line):
            found = True
            found_level = extract_evidence_level(line)
            break

    if not found:
        errors.append(f'missing Evidence Status (first 10 lines): {relative_to_root(path)}')
    return errors, found_level


def resolve_link(path: Path, target: str) -> Tuple[bool, str]:
    target = target.strip()
    if not target or target.startswith('#') or '://' in target or target.startswith('mailto:'):
        return True, ''
    clean_target = target.split('#', 1)[0]
    resolved = (path.parent / clean_target).resolve()
    return resolved.exists(), str(resolved)


def check_links(path: Path) -> List[str]:
    text = path.read_text(encoding='utf-8')
    errors: List[str] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1)
        ok, resolved = resolve_link(path, target)
        if not ok:
            errors.append(f'broken link: {relative_to_root(path)} -> {target}')
    return errors


def _looks_like_repo_path(candidate: str) -> bool:
    """Return True for inline-code path references that should resolve in this repo."""
    if any(ch in candidate for ch in ['*', '<', '>', '{', '}', '|', '$', ':', '#']):
        return False
    if ' ' in candidate:
        return False
    if not (
        candidate.endswith('.md')
        or candidate.endswith('.yaml')
        or candidate.endswith('/')
        or '/' in candidate
    ):
        return False
    if candidate.startswith(('../', './')):
        return True
    return candidate.split('/', 1)[0] in KNOWN_PATH_ROOTS


def resolve_code_path(path: Path, candidate: str) -> Tuple[bool, str]:
    candidate = candidate.strip()
    clean_candidate = candidate.split('#', 1)[0].rstrip('/')
    if candidate.startswith(('../', './')):
        resolved = (path.parent / clean_candidate).resolve()
    else:
        resolved = (ROOT / clean_candidate).resolve()
    return resolved.exists(), str(resolved)


def check_code_span_paths(path: Path) -> List[str]:
    """Check path-like inline code spans that are used as navigational references.

    Markdown links are already checked by check_links(). This catches common
    skill navigation references written as `architecture/foo.md`, where a stale
    path would otherwise be invisible to the validator.
    """
    text = path.read_text(encoding='utf-8')
    clean_text = '\n'.join(_strip_code_blocks(text.splitlines()))
    errors: List[str] = []
    for match in CODE_PATH_RE.finditer(clean_text):
        candidate = match.group(1).strip()
        if not _looks_like_repo_path(candidate):
            continue
        ok, _ = resolve_code_path(path, candidate)
        if not ok:
            errors.append(f'broken inline path: {relative_to_root(path)} -> {candidate}')
    return errors


def main() -> int:
    errors: List[str] = []
    total_files = 0
    valid_evidence = 0
    exempt_files = 0
    failing_files = 0
    level_counts: Counter = Counter()

    all_md = list(iter_markdown_files())
    total_files = len(all_md)

    files_with_errors: set = set()

    for path in all_md:
        rel = relative_to_root(path)

        # Exempt: templates
        if is_template(path):
            exempt_files += 1
            continue

        # Exempt: non-doc files in starter-kit (only .md reach here,
        # but __init__.py-like names are skipped)
        if rel.parts and rel.parts[0] == 'starter-kit' and rel.name == '__init__.py':
            exempt_files += 1
            continue

        evidence_errors, level = check_evidence_status(path)
        link_errors = check_links(path)
        code_path_errors = check_code_span_paths(path)

        if level is not None:
            valid_evidence += 1
            level_counts[level] += 1

        file_errors = evidence_errors + link_errors + code_path_errors
        if file_errors:
            files_with_errors.add(path)
            errors.extend(file_errors)

    # Starter-kit required files check
    starter_required = [
        ROOT / 'starter-kit/verified-tool-agent/README.md',
        ROOT / 'starter-kit/verified-tool-agent/agent_runtime.py',
        ROOT / 'starter-kit/verified-tool-agent/tests/test_runtime.py',
    ]
    for item in starter_required:
        if not item.exists():
            errors.append(f'missing starter-kit file: {relative_to_root(item)}')

    failing_files = len(files_with_errors)

    # --- Output ---
    if errors:
        print('VALIDATION FAILED')
        for err in errors:
            print(f'  - {err}')
        print()

    else:
        print('VALIDATION OK')
        print()

    # Summary statistics
    print('--- Summary ---')
    print(f'Total markdown files scanned: {total_files}')
    print(f'Files with valid Evidence Status: {valid_evidence}')
    print(f'Files exempt (templates, non-doc): {exempt_files}')
    print(f'Files failing: {failing_files}')

    if level_counts:
        print()
        print('Evidence Status distribution:')
        for level in sorted(level_counts, key=lambda l: -level_counts[l]):
            print(f'  {level}: {level_counts[level]}')

    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
