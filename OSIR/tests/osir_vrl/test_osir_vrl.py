import os

import pytest

# sys.path and OSIR_HOME are set up by tests/conftest.py
from osir_vrl.OsirVrlModel import OsirVrlModel
from osir_vrl.OsirVrlTransformation import OsirVrlTransformation
from osir_vrl.OsirVrlBlock import OsirVrlBlock
from pydantic import ValidationError

OSIR_SRC = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))
EXAMPLE_YML = os.path.join(OSIR_SRC, "osir_vrl", "examples", "custom_log.yml")


def _generate() -> str:
    return OsirVrlModel.from_yaml(EXAMPLE_YML).to_vrl()


def test_header_from_metadata():
    vrl = _generate()
    assert "# Module VRL : custom_log" in vrl
    assert "# Version    : 1.0" in vrl
    assert "# Type       : PARSER & NORMALIZER" in vrl
    assert "# Source     : tools=custom_app, internal=custom_log, raw=raw" in vrl


def test_transformations_are_linear():
    vrl = _generate()
    # items are rendered in YAML order: first item = first VRL instruction
    order = [
        "_result, err = parse_timestamp(.raw",  # 1st transformation (on_error: log)
        '.event.kind = "event"',                # 2nd
        "del(.payload)",                        # last (deletion)
    ]
    positions = [vrl.index(marker) for marker in order]
    assert positions == sorted(positions)


def test_operation_with_parameters():
    vrl = _generate()
    # default guard on a plain source field
    assert "if exists(.raw) {" in vrl


def test_fallible_operation_gets_error_handler_by_default():
    vrl = _generate()
    # no on_error needed: a call on an event field is fallible in VRL
    assert "_result, err = parse_timestamp(.raw, format: \"%Y-%m-%dT%H:%M:%SZ\", timezone: \"UTC\")" in vrl
    # assignment only on success, warning log otherwise, event never aborts
    assert "if err == null {\n    .timestamp = _result\n  } else {" in vrl
    assert 'log("[custom_log] échec de l\'opération parse_timestamp sur timestamp : " + err, level: "warn")' in vrl


def test_bang_operation_rendered_verbatim():
    vrl = _generate()
    # explicit aborting variant is respected, no error handler
    assert ".event.action = downcase!(.json_data.action)" in vrl
    assert "err = downcase" not in vrl


def test_infallible_operation_rendered_direct():
    t = OsirVrlTransformation(type="transformation", target="uid", operation="uuid_v4")
    # uuid_v4 cannot be destructured (E104): direct call
    assert t.to_vrl() == [".uid = uuid_v4()"]


def test_on_error_direct_renders_verbatim():
    t = OsirVrlTransformation(
        type="transformation", target="json_data", source="payload",
        operation="parse_json", on_error="direct",
    )
    assert t.to_vrl() == ["if exists(.payload) {", "  .json_data = parse_json(.payload)", "}"]


def test_on_error_log_on_infallible_rejected():
    with pytest.raises(ValidationError):
        OsirVrlTransformation(
            type="transformation", target="uid", operation="uuid_v4", on_error="log"
        )


def test_on_error_requires_operation():
    with pytest.raises(ValidationError):
        OsirVrlTransformation(type="normalization", target="a", source="b", on_error="log")


def test_translation_uses_parameters_dictionary():
    vrl = _generate()
    assert '"warn": "Warning",' in vrl
    assert '?? "Unknown"' in vrl


def test_deletion_without_combined_guard():
    vrl = _generate()
    # each deleted field is independent: no combined exists() guard
    assert "del(.payload)\ndel(.raw)" in vrl
    assert "exists(.payload) && exists(.raw)" not in vrl


def test_timeline_rendered_after_transformations():
    vrl = _generate()
    assert vrl.index("# timeline") > vrl.index("# transformations")
    assert ".message = " in vrl
    assert 'push!(.relationships, {"source": to_string!(.user.name)' in vrl


def test_unknown_type_rejected():
    with pytest.raises(ValidationError):
        OsirVrlTransformation(type="bogus", target="a", source="b")


def test_deletion_requires_source():
    with pytest.raises(ValidationError):
        OsirVrlTransformation(type="deletion")


def test_assignment_requires_target():
    with pytest.raises(ValidationError):
        OsirVrlTransformation(type="normalization", source="a")


def test_old_pipeline_format_rejected(tmp_path):
    # legacy pipeline/stages configs must fail loudly, not generate an empty VRL
    legacy = tmp_path / "legacy.yml"
    legacy.write_text(
        "metadata:\n"
        '  version: "1.0"\n'
        "  author: Typ\n"
        "  description: legacy\n"
        "pipeline:\n"
        "  - name: set_timestamp\n"
        "stages: {}\n"
    )
    with pytest.raises(ValidationError):
        OsirVrlModel.from_yaml(str(legacy))


def test_old_transformations_format_rejected(tmp_path):
    # the pre-block format (flat `transformations` list) must fail loudly
    legacy = tmp_path / "legacy.yml"
    legacy.write_text(
        "metadata:\n"
        '  version: "1.0"\n'
        "  author: Typ\n"
        "  description: legacy\n"
        "transformations:\n"
        "  - {target: a, source: b}\n"
    )
    with pytest.raises(ValidationError):
        OsirVrlModel.from_yaml(str(legacy))


# ── block format ─────────────────────────────────────────────────────────────

def test_set_shorthand_string_is_a_source():
    # a plain string spec is a source reference, not a literal value
    block = OsirVrlBlock.model_validate({"set": {"user.name": "json_data.user"}})
    lines = block.entries()[0].to_vrl()
    assert lines == ["if exists(.json_data.user) {", "  .user.name = .json_data.user", "}"]


def test_set_conditions_render_timeline_style_guard():
    vrl = _generate()
    # conditions on a set entry: equality guard around the assignment
    assert 'if .event.dataset == "custom_log" {' in vrl
    assert '.event.environment = "production"' in vrl


def test_conditions_without_value_render_exists():
    block = OsirVrlBlock.model_validate({
        "set": {"a": {"value": "x"}}, "conditions": [{"field": "b"}]
    })
    lines = block.entries()[0].to_vrl()
    assert lines == ["if exists(.b) {", '  .a = "x"', "}"]


def test_condition_exists_false_renders_negation():
    block = OsirVrlBlock.model_validate({
        "set": {"event": {"value": {}}},
        "conditions": [{"field": "event", "exists": False}],
    })
    lines = block.entries()[0].to_vrl()
    assert lines == ["if !exists(.event) {", "  .event = {}", "}"]


def test_condition_value_and_exists_rejected():
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({
            "set": {"a": "b"},
            "conditions": [{"field": "x", "value": "y", "exists": True}],
        })


def test_guard_dedup_filter_covering_source():
    # a filter already containing exists(.src) suppresses the default guard
    block = OsirVrlBlock.model_validate({
        "set": {"file.path": "to_string!(del(.FullPath))"},
        "filter": "exists(.FullPath) && !exists(.file.path)",
    })
    lines = block.entries()[0].to_vrl()
    assert lines == [
        "if exists(.FullPath) && !exists(.file.path) {",
        "  .file.path = to_string!(del(.FullPath))",
        "}",
    ]


def test_guard_no_dedup_on_negated_exists():
    # !exists(.x) does not cover the source: the default guard stays
    block = OsirVrlBlock.model_validate({
        "set": {"a": "b"}, "filter": "!exists(.a)",
    })
    lines = block.entries()[0].to_vrl()
    assert lines[0] == "if !exists(.a) && exists(.b) {"


def test_filter_and_conditions_combined():
    # block-level filter + conditions + default source guard, in this order
    block = OsirVrlBlock.model_validate({
        "set": {"a": "b"},
        "filter": "!is_null(.c)",
        "conditions": [{"field": "d", "value": 1}],
    })
    lines = block.entries()[0].to_vrl()
    assert lines[0] == "if !is_null(.c) && .d == 1 && exists(.b) {"


def test_block_filter_guards_every_entry():
    # a block-level filter applies to each entry of the block,
    # combined with the default source guard
    block = OsirVrlBlock.model_validate({
        "set": {"a": "x", "b": "y"}, "filter": "exists(.z)",
    })
    vrl = "\n".join(line for e in block.entries() for line in e.to_vrl())
    assert vrl.count("if exists(.z) && exists(") == 2


def test_translate_block_v1_structure():
    block = OsirVrlBlock.model_validate({
        "translate": {
            "mapping": {"action.name": "event.id"},
            "dictionary": {"4624": "logged on", "4625": "logon failure"},
            "fallback": "Unknown",
        }
    })
    lines = block.entries()[0].to_vrl()
    assert any('"4624": "logged on"' in line for line in lines)
    assert '?? "Unknown"' in "\n".join(lines)


def test_translate_block_multiple_targets_share_dictionary():
    block = OsirVrlBlock.model_validate({
        "translate": {
            "mapping": {"a": "x", "b": "x"},
            "dictionary": {"k": "v"},
        }
    })
    assert len(block.entries()) == 2
    for e in block.entries():
        assert e.dictionary == {"k": "v"}


def test_translate_block_requires_mapping_and_dictionary():
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"translate": {"mapping": {"a": "b"}}})
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"translate": {"dictionary": {"a": "b"}}})
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"translate": {"mapping": {"a": "b"}, "dictionary": {}, "bogus": 1}})


def test_delete_block_renders_del_per_field():
    block = OsirVrlBlock.model_validate({"delete": ["payload", "raw"]})
    assert block.entries()[0].to_vrl() == ["del(.payload)", "del(.raw)"]


def test_delete_block_level_filter():
    block = OsirVrlBlock.model_validate({
        "delete": ["threat.technique.id_name"],
        "filter": "is_empty(to_string!(.threat.technique.id_name))",
    })
    lines = block.entries()[0].to_vrl()
    assert lines[0].startswith("if is_empty(to_string!(.threat.technique.id_name)) {")
    assert "  del(.threat.technique.id_name)" in lines


def test_custom_block_with_filter():
    block = OsirVrlBlock.model_validate({
        "custom": '.a = "x"',
        "filter": "exists(.a)",
    })
    assert block.entries()[0].to_vrl() == ["if exists(.a) {", '  .a = "x"', "}"]


def test_block_requires_exactly_one_kind():
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"set": {"a": "b"}, "delete": ["c"]})
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({})


def test_entry_level_filter_rejected_on_set():
    # guards live on the block, next to the kind key, never inside an entry
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"set": {"a": {"source": "b", "filter": "exists(.b)"}}})
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"set": {"a": {"source": "b", "conditions": [{"field": "c"}]}}})


def test_block_entries_preserve_mapping_order():
    block = OsirVrlBlock.model_validate({"set": {"a": "x1", "b": "x2", "c": "x3"}})
    vrl = "\n".join(line for e in block.entries() for line in e.to_vrl())
    assert vrl.index(".a = ") < vrl.index(".b = ") < vrl.index(".c = ")


# ── timeline relationships (root section, attached by timeline id) ────────────

def _write_cfg(tmp_path, timeline: str, relationships: str = ""):
    cfg = tmp_path / "cfg.yml"
    cfg.write_text(
        "metadata:\n"
        '  version: "1.0"\n'
        "  author: Typ\n"
        "  description: test\n"
        "transformation:\n"
        "  - set:\n"
        "      event.kind:\n"
        "        value: event\n"
        "timeline:\n"
        f"{timeline}"
        + (f"\nrelationships:\n{relationships}" if relationships else "")
    )
    return str(cfg)


def test_relationship_attached_to_timeline_entry_by_id(tmp_path):
    timeline = (
        "  - id: logon\n"
        '    message: "{user.name} logged on to {host.name}"\n'
        "    conditions:\n"
        "      - field: event.id\n"
        "        value: 4624\n"
    )
    relationships = (
        "  - id: logon\n"
        "    source: user.name\n"
        "    target: host.name\n"
        "    type: logged on to\n"
    )
    vrl = OsirVrlModel.from_yaml(_write_cfg(tmp_path, timeline, relationships)).to_vrl()
    assert 'push!(.relationships, {"source": to_string!(.user.name)' in vrl
    # the push is rendered inside the guarded block of its timeline entry
    assert vrl.index(".event.id == 4624") < vrl.index("push!(.relationships")


def test_relationship_without_matching_timeline_entry_rejected(tmp_path):
    timeline = (
        "  - id: logon\n"
        '    message: "{user.name} logged on to {host.name}"\n'
    )
    relationships = (
        "  - id: logoff\n"
        "    source: user.name\n"
        "    target: host.name\n"
        "    type: logged off from\n"
    )
    with pytest.raises(ValidationError):
        OsirVrlModel.from_yaml(_write_cfg(tmp_path, timeline, relationships))


def test_duplicate_timeline_id_rejected(tmp_path):
    timeline = (
        "  - id: logon\n"
        '    message: "{user.name} logged on to {host.name}"\n'
        "  - id: logon\n"
        '    message: "{user.name} logged on to {host.name} again"\n'
    )
    with pytest.raises(ValidationError):
        OsirVrlModel.from_yaml(_write_cfg(tmp_path, timeline))


def test_inline_timeline_relationships_rejected(tmp_path):
    # relationships no longer live inside a timeline entry
    timeline = (
        '  - message: "{user.name} logged on to {host.name}"\n'
        "    relationships:\n"
        "      - id: logon\n"
        "        source: user.name\n"
        "        target: host.name\n"
        "        type: logged on to\n"
    )
    with pytest.raises(ValidationError):
        OsirVrlModel.from_yaml(_write_cfg(tmp_path, timeline))


# ── constant blocks (literal-value shorthand) ─────────────────────────────────

def test_constant_block_renders_literal_assignments():
    block = OsirVrlBlock.model_validate({"constant": {
        "event.dataset": "windows.shellbags",
        "event.kind": "state",
        "event.category": ["file"],
        "event.outcome": True,
        "event.code": 4624,
    }})
    entries = block.entries()
    assert [e.target for e in entries] == [
        "event.dataset", "event.kind", "event.category", "event.outcome", "event.code"]
    vrl = "\n".join(line for e in entries for line in e.to_vrl())
    # direct assignments, no default source guard on a value
    assert '.event.dataset = "windows.shellbags"' in vrl
    assert '.event.kind = "state"' in vrl
    assert '.event.category = ["file"]' in vrl
    assert ".event.outcome = true" in vrl
    assert ".event.code = 4624" in vrl
    assert "exists(" not in vrl


def test_constant_string_is_a_value_not_a_source():
    # the opposite of the set shorthand: a plain string is a literal
    block = OsirVrlBlock.model_validate({"constant": {"event.module": "windows"}})
    entry = block.entries()[0]
    assert entry.value == "windows"
    assert entry.source is None


def test_constant_block_level_guard():
    block = OsirVrlBlock.model_validate({
        "constant": {"event.environment": "production"},
        "conditions": [{"field": "event.dataset", "value": "custom_log"}],
    })
    lines = block.entries()[0].to_vrl()
    assert lines == [
        'if .event.dataset == "custom_log" {',
        '  .event.environment = "production"',
        "}",
    ]


def test_constant_block_takes_at_least_one_target():
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({"constant": {}})


def test_constant_block_requires_exactly_one_kind():
    with pytest.raises(ValidationError):
        OsirVrlBlock.model_validate({
            "constant": {"a": "x"}, "delete": ["b"],
        })
