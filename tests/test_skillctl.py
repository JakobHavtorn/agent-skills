#!/usr/bin/env python3
"""Tests for pure functions in bin/skillctl.

Runnable standalone (``python3 tests/test_skillctl.py``) or via pytest.
"""

import json
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


def test_extract_omp_text_string_content():
    """turn_end.message.content may be a bare string."""
    ndjson = '{"type":"turn_end","message":{"role":"assistant","content":"api-designer"}}\n'
    assert skillctl._extract_omp_text(ndjson) == "api-designer"


def test_extract_omp_text_empty():
    """Non-matching events and malformed lines yield empty text."""
    assert skillctl._extract_omp_text("not json\n{}\n") == ""


# ---------------------------------------------------------------------------
# sync — sources, pins, provenance, classification, validation
# ---------------------------------------------------------------------------

load_sources = skillctl.load_sources
covered_by_include = skillctl.covered_by_include
parse_pin_url = skillctl.parse_pin_url
normalize_provenance = skillctl.normalize_provenance
apply_provenance = skillctl.apply_provenance
classify_vendored_skill = skillctl.classify_vendored_skill
validate_materialized_skill = skillctl.validate_materialized_skill
insert_readme_row = skillctl.insert_readme_row
files_under = skillctl.files_under
pin_skip_detail = skillctl.pin_skip_detail

PIN_OLD = "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"
PIN_NEW = "0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0"
PIN_OLD_URL = f"https://github.com/example/skills/tree/{PIN_OLD}/skills/demo"
PIN_NEW_URL = f"https://github.com/example/skills/tree/{PIN_NEW}/skills/demo"


def _write_skill(directory, body="Original body.\n", provenance=True, extra_files=None):
    """Minimal skill dir; provenance=True mirrors a vendored local copy."""
    directory.mkdir(parents=True, exist_ok=True)
    if provenance:
        frontmatter = (
            "---\nname: demo\ndescription: A demo skill.\n"
            f"license: MIT\nmetadata:\n  vendored-from: {PIN_OLD_URL}\n---\n\n"
        )
    else:
        frontmatter = "---\nname: demo\ndescription: A demo skill.\n---\n\n"
    (directory / "SKILL.md").write_text(frontmatter + body)
    for name, content in (extra_files or {}).items():
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def test_load_sources_parses_manifest():
    """Sources from plugin.json parse into SourceConfig records."""
    tmp = Path(tempfile.mkdtemp())
    plugin = tmp / "plugins" / "demo"
    (plugin / "skills").mkdir(parents=True)
    (plugin / "plugin.json").write_text(
        json.dumps(
            {
                "name": "demo",
                "sources": [{"repo": "acme/skills", "policy": "track", "include": ["skills/*"], "license": "MIT"}],
            }
        )
    )
    sources = load_sources(tmp)
    assert len(sources) == 1
    assert (sources[0].plugin, sources[0].repo, sources[0].policy, sources[0].license) == (
        "demo",
        "acme/skills",
        "track",
        "MIT",
    )


def test_load_sources_rejects_bad_policy():
    """Unknown policy raises SkillctlError."""
    tmp = Path(tempfile.mkdtemp())
    plugin = tmp / "plugins" / "demo"
    plugin.mkdir(parents=True)
    (plugin / "plugin.json").write_text(
        json.dumps({"name": "demo", "sources": [{"repo": "acme/skills", "policy": "auto", "include": ["skills/*"]}]})
    )
    try:
        load_sources(tmp)
    except skillctl.SkillctlError:
        pass
    else:
        raise AssertionError("expected SkillctlError for unknown policy")


def test_covered_by_include_exact_and_glob():
    """Exact paths and globs both match; unrelated paths do not."""
    assert covered_by_include("skills/engineering/tdd", ["skills/engineering/tdd"])
    assert covered_by_include("skills/grafana-core/promql", ["skills/grafana-core/*"])
    assert not covered_by_include("skills/engineering/tdd", ["skills/productivity/*"])


def test_parse_pin_url():
    """Pinned tree URLs split into repo, commit, path."""
    pin = parse_pin_url(PIN_OLD_URL)
    assert pin == {"repo": "example/skills", "commit": PIN_OLD, "path": "skills/demo"}


def test_normalize_provenance_strips_injections():
    """license + vendored-from + emptied metadata normalize away."""
    local = f"---\nname: d\nlicense: MIT\nmetadata:\n  vendored-from: {PIN_OLD_URL}\n---\nBody.\n"
    upstream = "---\nname: d\n---\nBody.\n"
    assert normalize_provenance(local) == normalize_provenance(upstream)


def test_normalize_provenance_keeps_populated_metadata():
    """A metadata block with other children survives normalization."""
    text = "---\nname: d\nmetadata:\n  credits:\n    author: A\n---\n"
    assert normalize_provenance(text) == text


def test_apply_provenance_adds_license_and_metadata():
    """Upstream without license/metadata gets both injected (pocock shape)."""
    upstream = "---\nname: demo\ndescription: A demo skill.\n---\n\nBody.\n"
    out = apply_provenance(upstream, PIN_NEW_URL, "MIT")
    assert "license: MIT" in out
    assert f"metadata:\n  vendored-from: {PIN_NEW_URL}" in out
    assert out.startswith("---\nname: demo")


def test_apply_provenance_appends_into_existing_metadata():
    """vendored-from lands inside an existing metadata block (credits shape)."""
    upstream = "---\nname: d\ndescription: d\nmetadata:\n  credits:\n    author: A\n---\n\nBody.\n"
    out = apply_provenance(upstream, PIN_NEW_URL, None)
    assert out.index("  credits:") < out.index(f"  vendored-from: {PIN_NEW_URL}")
    assert "license" not in out


def test_apply_provenance_replaces_existing_pin():
    """An existing pin URL is refreshed; license and metadata stay single (grafana shape)."""
    local = (
        f"---\nname: d\nlicense: Apache-2.0\ndescription: d\nmetadata:\n  vendored-from: {PIN_OLD_URL}\n---\nBody.\n"
    )
    out = apply_provenance(local, PIN_NEW_URL, "Apache-2.0")
    assert PIN_NEW_URL in out and PIN_OLD_URL not in out
    assert out.count("license:") == 1
    assert out.count("metadata:") == 1


def test_classify_clean_skill():
    """Local copy equal to upstream at the pin (provenance aside) classifies clean."""
    root = Path(tempfile.mkdtemp())
    local = root / "local"
    _write_skill(local, provenance=True)
    old_root = root / "old"
    _write_skill(old_root / "skills" / "demo", provenance=False)
    head_root = root / "head"
    _write_skill(head_root / "skills" / "demo", body="New upstream body.\n", provenance=False)
    state, detail = classify_vendored_skill({"commit": PIN_OLD, "path": "skills/demo"}, local, old_root, head_root)
    assert state == "clean"
    assert detail == ""


def test_classify_adapted_skill():
    """A hand-edited body classifies adapted, naming the deviating file."""
    root = Path(tempfile.mkdtemp())
    local = root / "local"
    _write_skill(local, body="Hand-edited body.\n", provenance=True)
    old_root = root / "old"
    _write_skill(old_root / "skills" / "demo", provenance=False)
    head_root = root / "head"
    _write_skill(head_root / "skills" / "demo", provenance=False)
    state, detail = classify_vendored_skill({"commit": PIN_OLD, "path": "skills/demo"}, local, old_root, head_root)
    assert state == "adapted"
    assert "SKILL.md" in detail


def test_classify_local_extra_file_is_adapted():
    """A file that exists only locally marks the skill adapted."""
    root = Path(tempfile.mkdtemp())
    local = root / "local"
    _write_skill(local, provenance=True, extra_files={"CREDITS.md": "x"})
    old_root = root / "old"
    _write_skill(old_root / "skills" / "demo", provenance=False)
    head_root = root / "head"
    _write_skill(head_root / "skills" / "demo", provenance=False)
    state, _detail = classify_vendored_skill({"commit": PIN_OLD, "path": "skills/demo"}, local, old_root, head_root)
    assert state == "adapted"


def test_classify_deleted_upstream():
    """A pin path gone from the head tree classifies deleted."""
    root = Path(tempfile.mkdtemp())
    local = root / "local"
    _write_skill(local, provenance=True)
    old_root = root / "old"
    _write_skill(old_root / "skills" / "demo", provenance=False)
    head_root = root / "head"
    head_root.mkdir()
    state, _detail = classify_vendored_skill({"commit": PIN_OLD, "path": "skills/demo"}, local, old_root, head_root)
    assert state == "deleted"


def test_validate_clean_skill():
    """A well-formed skill passes the local battery."""
    root = Path(tempfile.mkdtemp())
    skill = root / "demo"
    _write_skill(skill, provenance=True, extra_files={"references/notes.md": "safe text\n"})
    assert validate_materialized_skill(skill) == []


def test_validate_flags_hygiene_problems():
    """Digit runs, IBAN shapes, and data files are flagged."""
    root = Path(tempfile.mkdtemp())
    skill = root / "demo"
    _write_skill(
        skill,
        provenance=True,
        extra_files={
            "references/data.md": "id 123456789012\n",
            "references/iban.md": "acct DK123456789012345\n",
            "dump.csv": "x",
        },
    )
    problems = validate_materialized_skill(skill)
    assert any("digit run" in problem for problem in problems)
    assert any("IBAN-shaped" in problem for problem in problems)
    assert any("data file" in problem for problem in problems)


def test_validate_flags_broken_reference():
    """A SKILL.md reference to a missing file is flagged."""
    root = Path(tempfile.mkdtemp())
    skill = root / "demo"
    _write_skill(skill, body="See references/missing.md for more.\n", provenance=True)
    problems = validate_materialized_skill(skill)
    assert any("broken reference references/missing.md" in problem for problem in problems)


def test_validate_flags_long_skill_md():
    """A SKILL.md past the line limit is flagged."""
    root = Path(tempfile.mkdtemp())
    skill = root / "demo"
    _write_skill(skill, body="line\n" * 600, provenance=True)
    problems = validate_materialized_skill(skill)
    assert any("lines (max 500)" in problem for problem in problems)


def test_validate_exempts_provenance_pins():
    """A pin sha containing a 12+ digit run does not fail the battery."""
    root = Path(tempfile.mkdtemp())
    skill = root / "demo"
    long_run_sha = "a" * 28 + "123456789012"  # 40 hex chars ending in a 12-digit run
    _write_skill(skill, provenance=True)
    pin = skill / "SKILL.md"
    pin.write_text(pin.read_text().replace(PIN_OLD, long_run_sha))
    assert validate_materialized_skill(skill) == []


def test_validate_flags_digit_runs_outside_pins():
    """A digit run in the body still fails the battery."""
    root = Path(tempfile.mkdtemp())
    skill = root / "demo"
    _write_skill(skill, body="timestamp 123456789012\n", provenance=True)
    problems = validate_materialized_skill(skill)
    assert any("digit run" in problem for problem in problems)


def test_files_under_filters_by_path():
    """Only compare-API files under the skill's upstream path count as drift."""
    files = ["skills/demo/SKILL.md", "skills/other/SKILL.md", "README.md"]
    assert files_under(files, "skills/demo") == ["skills/demo/SKILL.md"]


def test_pin_skip_detail_states():
    """Pin annotation distinguishes drift, truncated compares, and quiet moves."""
    pin = {"commit": PIN_OLD, "path": "skills/demo"}
    assert pin_skip_detail(pin, [], False) == "upstream moved, no changes under the skill"
    assert "compare truncated" in pin_skip_detail(pin, [], True)
    detail = pin_skip_detail(pin, ["skills/demo/SKILL.md"], False)
    assert detail.startswith(f"DRIFT: 1 upstream file(s) changed since {PIN_OLD[:7]}")
    assert "3+" in pin_skip_detail(pin, ["a", "b", "c"], True)


def test_insert_readme_row_alphabetical():
    """A row lands between its alphabetical neighbours in the plugin table."""
    readme = (
        "### `demo`\n\n| Skill | Description |\n|---|---|\n"
        "| [alpha](plugins/demo/skills/alpha) | A |\n"
        "| [zeta](plugins/demo/skills/zeta) | Z |\n"
    )
    out = insert_readme_row(readme, "demo", "mid", "| [mid](plugins/demo/skills/mid) | M |")
    assert out.index("alpha") < out.index("mid") < out.index("zeta")


# ---------------------------------------------------------------------------
# opencode /command wrappers for user-invoked skills
# ---------------------------------------------------------------------------

get_frontmatter_field = skillctl.get_frontmatter_field
is_user_invoked = skillctl.is_user_invoked
render_command_wrapper = skillctl.render_command_wrapper
is_managed_command = skillctl.is_managed_command
link_user_invoked_commands = skillctl.link_user_invoked_commands
unlink_command_wrappers = skillctl.unlink_command_wrappers
COMMAND_MARKER = skillctl.COMMAND_MARKER


def _write_skill_dir(root, name, user_invoked=False):
    """Minimal skill dir with an optional user-invoked flag."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    flag = "disable-model-invocation: true\n" if user_invoked else ""
    (skill_dir / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Skill {name}\n{flag}---\n\nBody.\n")
    return skill_dir


def _linked_target(root, skill_dirs):
    """Fake harness skills dir with every skill linked by name."""
    skills_target = root / "skills"
    skills_target.mkdir()
    for skill_dir in skill_dirs:
        (skills_target / skill_dir.name).symlink_to(skill_dir)
    return skills_target


def test_frontmatter_field_reads_top_level_scalars():
    """Top-level keys parse; missing keys return None."""
    root = Path(tempfile.mkdtemp())
    skill = _write_skill_dir(root, "demo", user_invoked=True)
    assert get_frontmatter_field(skill, "name") == "demo"
    assert get_frontmatter_field(skill, "description") == "Skill demo"
    assert get_frontmatter_field(skill, "disable-model-invocation") == "true"
    assert get_frontmatter_field(skill, "missing") is None


def test_frontmatter_field_ignores_indented_keys():
    """Keys nested under metadata: never read as top-level."""
    root = Path(tempfile.mkdtemp())
    skill = root / "nested"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: nested\ndescription: d\nmetadata:\n  disable-model-invocation: true\n---\n\nBody.\n"
    )
    assert get_frontmatter_field(skill, "disable-model-invocation") is None
    assert is_user_invoked(skill) is False


def test_frontmatter_field_strips_quotes():
    """Quoted scalar values lose their surrounding quotes."""
    root = Path(tempfile.mkdtemp())
    skill = root / "quoted"
    skill.mkdir()
    (skill / "SKILL.md").write_text('---\nname: q\ndescription: "Quoted: description"\n---\n\nBody.\n')
    assert get_frontmatter_field(skill, "description") == "Quoted: description"


def test_is_user_invoked_without_flag():
    """A skill without the flag is machine-invocable."""
    root = Path(tempfile.mkdtemp())
    skill = _write_skill_dir(root, "plain")
    assert is_user_invoked(skill) is False


def test_render_command_wrapper_shape():
    """Wrapper carries frontmatter, marker, load line, and $ARGUMENTS."""
    content = render_command_wrapper("grill-me", "Sharpen a plan: interview")
    assert content.startswith("---\n")
    assert 'description: "Sharpen a plan: interview"' in content
    assert COMMAND_MARKER in content
    assert "Load the `grill-me` skill and follow its instructions." in content
    assert content.rstrip().endswith("$ARGUMENTS")


def test_render_command_wrapper_without_description():
    """No description means no description line in the wrapper."""
    content = render_command_wrapper("x", None)
    assert "description:" not in content
    assert "Load the `x` skill" in content


def test_is_managed_command_detects_marker():
    """Only files containing the marker count as skillctl-generated."""
    root = Path(tempfile.mkdtemp())
    managed = root / "managed.md"
    managed.write_text(f"---\n{COMMAND_MARKER}\n---\n\nLoad.\n")
    external = root / "external.md"
    external.write_text("---\ndescription: hand-written\n---\n\nDo things.\n")
    assert is_managed_command(managed) is True
    assert is_managed_command(external) is False
    assert is_managed_command(root / "missing.md") is False


def test_link_commands_wraps_only_user_invoked_skills():
    """One wrapper per user-invoked linked skill; nothing for the rest."""
    root = Path(tempfile.mkdtemp())
    asked_for = _write_skill_dir(root, "asked-for", user_invoked=True)
    auto = _write_skill_dir(root, "auto")
    skills_target = _linked_target(root, [asked_for, auto])
    commands_dir = root / "commands"

    written, removed = link_user_invoked_commands({"demo": [asked_for, auto]}, skills_target, commands_dir)

    assert (written, removed) == (1, 0)
    wrapper = commands_dir / "asked-for.md"
    assert is_managed_command(wrapper)
    assert "Load the `asked-for` skill" in wrapper.read_text()
    assert not (commands_dir / "auto.md").exists()


def test_link_commands_skips_unlinked_skill():
    """No wrapper when the skill is not linked in the skills dir."""
    root = Path(tempfile.mkdtemp())
    asked_for = _write_skill_dir(root, "asked-for", user_invoked=True)
    skills_target = root / "skills"
    skills_target.mkdir()

    written, removed = link_user_invoked_commands({"demo": [asked_for]}, skills_target, root / "commands")

    assert (written, removed) == (0, 0)
    assert not (root / "commands" / "asked-for.md").exists()


def test_link_commands_idempotent():
    """A second run writes nothing and leaves content unchanged."""
    root = Path(tempfile.mkdtemp())
    asked_for = _write_skill_dir(root, "asked-for", user_invoked=True)
    skills_target = _linked_target(root, [asked_for])
    commands_dir = root / "commands"
    link_user_invoked_commands({"demo": [asked_for]}, skills_target, commands_dir)
    before = (commands_dir / "asked-for.md").read_text()

    written, removed = link_user_invoked_commands({"demo": [asked_for]}, skills_target, commands_dir)

    assert (written, removed) == (0, 0)
    assert (commands_dir / "asked-for.md").read_text() == before


def test_link_commands_updates_changed_description():
    """A changed SKILL.md description regenerates the wrapper."""
    root = Path(tempfile.mkdtemp())
    asked_for = _write_skill_dir(root, "asked-for", user_invoked=True)
    skills_target = _linked_target(root, [asked_for])
    commands_dir = root / "commands"
    link_user_invoked_commands({"demo": [asked_for]}, skills_target, commands_dir)

    skill_md = asked_for / "SKILL.md"
    skill_md.write_text(skill_md.read_text().replace("Skill asked-for", "A better description"))
    written, removed = link_user_invoked_commands({"demo": [asked_for]}, skills_target, commands_dir)

    assert (written, removed) == (1, 0)
    assert "A better description" in (commands_dir / "asked-for.md").read_text()


def test_link_commands_skips_handwritten_wrapper():
    """A hand-written file at the target name is left untouched."""
    root = Path(tempfile.mkdtemp())
    asked_for = _write_skill_dir(root, "asked-for", user_invoked=True)
    skills_target = _linked_target(root, [asked_for])
    commands_dir = root / "commands"
    commands_dir.mkdir()
    handwritten = commands_dir / "asked-for.md"
    handwritten.write_text("---\ndescription: mine\n---\n\nMy custom command.\n")

    written, removed = link_user_invoked_commands({"demo": [asked_for]}, skills_target, commands_dir)

    assert (written, removed) == (0, 0)
    assert handwritten.read_text() == "---\ndescription: mine\n---\n\nMy custom command.\n"


def test_link_commands_removes_orphans_keeps_external():
    """Managed wrappers for gone skills are removed; foreign files stay."""
    root = Path(tempfile.mkdtemp())
    auto = _write_skill_dir(root, "auto")
    skills_target = _linked_target(root, [auto])
    commands_dir = root / "commands"
    commands_dir.mkdir()
    orphan = commands_dir / "renamed-away.md"
    orphan.write_text(render_command_wrapper("renamed-away", "Gone skill"))
    external = commands_dir / "keep-me.md"
    external.write_text("---\ndescription: plannotator\n---\n\nNot ours.\n")

    written, removed = link_user_invoked_commands({"demo": [auto]}, skills_target, commands_dir)

    assert (written, removed) == (0, 1)
    assert not orphan.exists()
    assert external.read_text() == "---\ndescription: plannotator\n---\n\nNot ours.\n"


def test_unlink_commands_removes_only_managed():
    """Unlink removes skillctl wrappers, never hand-written files."""
    root = Path(tempfile.mkdtemp())
    asked_for = _write_skill_dir(root, "asked-for", user_invoked=True)
    commands_dir = root / "commands"
    commands_dir.mkdir()
    managed = commands_dir / "asked-for.md"
    managed.write_text(render_command_wrapper("asked-for", "Skill asked-for"))
    handwritten = commands_dir / "handmade.md"
    handwritten.write_text("---\ndescription: mine\n---\n\nMy custom command.\n")

    removed = unlink_command_wrappers({"demo": [asked_for]}, commands_dir)

    assert removed == 1
    assert not managed.exists()
    assert handwritten.exists()


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
