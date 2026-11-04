#!/usr/bin/env python3
"""Tests for pure functions in bin/skillctl.

Runnable standalone (``python3 tests/test_skillctl.py``) or via pytest.
"""

import sys
import tempfile
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLCTL_PATH = REPO_ROOT / "bin" / "skillctl"


def _load_skillctl():
    """Load bin/skillctl as a module (it has no .py extension)."""
    mod = types.ModuleType("skillctl")
    mod.__file__ = str(SKILLCTL_PATH)
    sys.modules["skillctl"] = mod
    exec(compile(SKILLCTL_PATH.read_text(), str(SKILLCTL_PATH), "exec"), mod.__dict__)
    return mod


skillctl = _load_skillctl()

_classify_target_entry = skillctl._classify_target_entry
parse_skill_names = skillctl.parse_skill_names
build_classification_prompt = skillctl.build_classification_prompt


# ---------------------------------------------------------------------------
# _classify_target_entry — all 7 categories
# ---------------------------------------------------------------------------


def test_alive_symlink():
    """alive: symlink resolving to an existing dir inside the source repo."""
    tmp = (Path(tempfile.mkdtemp()) / "root").resolve()
    (tmp / "skills" / "my-skill").mkdir(parents=True)
    link = tmp / "skills" / "link"
    link.symlink_to(tmp / "skills" / "my-skill")
    cls, _ = _classify_target_entry(link, tmp, {"my-skill"})
    assert cls == "alive"


def test_foreign_alive_symlink():
    """foreign-alive: symlink resolving to an existing dir outside the repo."""
    tmp = Path(tempfile.mkdtemp()) / "root"
    tmp.mkdir()
    outside = Path(tempfile.mkdtemp()) / "other"
    outside.mkdir()
    link = tmp / "link"
    link.symlink_to(outside)
    cls, _ = _classify_target_entry(link, tmp, set())
    assert cls == "foreign-alive"


def test_stale_symlink():
    """stale: dangling symlink with target inside the source repo."""
    tmp = (Path(tempfile.mkdtemp()) / "root").resolve()
    tmp.mkdir()
    link = tmp / "link"
    link.symlink_to(tmp / "nonexistent")
    cls, _ = _classify_target_entry(link, tmp, set())
    assert cls == "stale"


def test_foreign_dangling_symlink():
    """foreign-dangling: dangling symlink with target outside the repo."""
    tmp = Path(tempfile.mkdtemp()) / "root"
    tmp.mkdir()
    outside = Path(tempfile.mkdtemp()) / "outside"
    link = tmp / "link"
    link.symlink_to(outside / "nonexistent")
    cls, _ = _classify_target_entry(link, tmp, set())
    assert cls == "foreign-dangling"


def test_copy_directory():
    """copy: real dir with SKILL.md whose name is a declared skill."""
    tmp = Path(tempfile.mkdtemp()) / "root"
    tmp.mkdir()
    entry = tmp / "my-skill"
    entry.mkdir()
    (entry / "SKILL.md").write_text("test")
    cls, _ = _classify_target_entry(entry, tmp, {"my-skill"})
    assert cls == "copy"


def test_orphan_directory():
    """orphan: real dir with SKILL.md whose name is NOT declared."""
    tmp = Path(tempfile.mkdtemp()) / "root"
    tmp.mkdir()
    entry = tmp / "unknown-skill"
    entry.mkdir()
    (entry / "SKILL.md").write_text("test")
    cls, _ = _classify_target_entry(entry, tmp, {"my-skill"})
    assert cls == "orphan"


def test_stray_directory():
    """stray: directory without SKILL.md."""
    tmp = Path(tempfile.mkdtemp()) / "root"
    tmp.mkdir()
    entry = tmp / "stray-dir"
    entry.mkdir()
    cls, _ = _classify_target_entry(entry, tmp, set())
    assert cls == "stray"


def test_stray_file():
    """stray: plain file."""
    tmp = Path(tempfile.mkdtemp()) / "root"
    tmp.mkdir()
    entry = tmp / "file.txt"
    entry.write_text("hello")
    cls, _ = _classify_target_entry(entry, tmp, set())
    assert cls == "stray"


# ---------------------------------------------------------------------------
# parse_skill_names
# ---------------------------------------------------------------------------


def test_parse_known_skill_names():
    """Parses known skill names from LLM response."""
    skills = [{"name": "open-pr"}, {"name": "code-review"}, {"name": "tdd"}]
    response = "open-pr\ncode-review\n"
    result = parse_skill_names(response, skills)
    assert result == {"open-pr", "code-review"}


def test_parse_none_response():
    """'none' response yields empty set."""
    skills = [{"name": "open-pr"}, {"name": "code-review"}]
    result = parse_skill_names("none", skills)
    assert result == set()


def test_parse_partial_matches():
    """Only known names are returned; unknown names are ignored."""
    skills = [{"name": "open-pr"}, {"name": "code-review"}]
    response = "open-pr\nunknown-skill\n"
    result = parse_skill_names(response, skills)
    assert result == {"open-pr"}


def test_parse_strips_dashes():
    """Lines with leading dashes (markdown list style) are stripped."""
    skills = [{"name": "open-pr"}]
    response = "- open-pr\n"
    result = parse_skill_names(response, skills)
    assert result == {"open-pr"}


# ---------------------------------------------------------------------------
# build_classification_prompt
# ---------------------------------------------------------------------------


def test_prompt_includes_skill_names():
    """Prompt lists all skill names."""
    skills = [{"name": "open-pr", "description": "Open a PR"}, {"name": "tdd", "description": "Test driven dev"}]
    prompt = build_classification_prompt(skills, "help me open a PR")
    assert "open-pr" in prompt
    assert "tdd" in prompt
    assert "Open a PR" in prompt
    assert "Test driven dev" in prompt


def test_prompt_includes_user_message():
    """Prompt includes the user's message."""
    skills = [{"name": "open-pr", "description": "Open a PR"}]
    prompt = build_classification_prompt(skills, "please create a pull request")
    assert "please create a pull request" in prompt


def test_prompt_includes_instruction():
    """Prompt instructs the LLM to reply with skill names or 'none'."""
    skills = [{"name": "open-pr", "description": "Open a PR"}]
    prompt = build_classification_prompt(skills, "test")
    assert "none" in prompt


def test_extract_omp_text_turn_end():
    """omp --mode json emits assistant text in turn_end.message.content."""
    ndjson = (
        '{"type":"turn_end","message":{"role":"assistant","content":'
        '[{"type":"text","text":"api-designer"}]}}\n'
        '{"type":"agent_end","messages":[{"role":"assistant","content":'
        '[{"type":"text","text":"api-designer"}]}]}\n'
        '{"type":"advisor_yielded"}\n'
    )
    assert skillctl._extract_omp_text(ndjson) == "api-designer"


def test_extract_omp_text_message_end():
    """Older omp builds emit text directly in message_end.content."""
    ndjson = '{"type":"message_end","content":"api-designer"}\n'
    assert skillctl._extract_omp_text(ndjson) == "api-designer"


def test_extract_omp_text_empty():
    """Non-matching events and malformed lines yield empty text."""
    assert skillctl._extract_omp_text("not json\n{}\n") == ""


# ---------------------------------------------------------------------------
# Runner — allow ``python3 tests/test_skillctl.py``
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _failed = 0
    for _name, _func in sorted(globals().items()):
        if _name.startswith("test_") and callable(_func):
            try:
                _func()
                print(f"  PASS {_name}")
            except AssertionError as e:
                print(f"  FAIL {_name}: {e}")
                _failed += 1
            except Exception as e:
                print(f"  ERROR {_name}: {e}")
                _failed += 1
    if _failed:
        print(f"\n{_failed} test(s) failed")
        sys.exit(1)
    print("\nAll tests passed")
