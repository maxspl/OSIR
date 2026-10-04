"""Generate a generic documentation page for every OSIR module.

Scans the module YAML files under ../OSIR/configs/modules and produces:
  - source/modules/<category>[/<subcategory>]/<module_name>.rst
    one generic page per module, built from a common template
  - source/modules/index.rst
    the Modules section landing page, listing every module by category

Categories 'test' and 'deprecated' are skipped.
Run from the docs/ directory, like modules_summary.py.
"""

import html as html_mod
import os
import posixpath
import re
import shutil

import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
MODULES_SRC = os.path.normpath(
    os.path.join(BASE, "..", "OSIR", "configs", "modules")
)
TRANSFORM_V2 = os.path.normpath(
    os.path.join(BASE, "..", "OSIR", "configs", "dependencies", "transform_v2")
)
OUT_DIR = os.path.join(BASE, "source", "modules")

SKIP_CATEGORIES = {"test", "deprecated"}

CATEGORY_TITLES = {
    "common": "Common",
    "connector": "Connector",
    "network": "Network",
    "pre_process": "Pre process",
    "scan": "Scan",
    "splunk": "Splunk",
    "unix": "Unix",
    "windows": "Windows",
}

TEMPLATE = """{title}
{title_underline}

{ingestion_tip}

Description
-----------

{description}

Timeline
--------

{timeline_section}

Relationships
-------------

{relationships_section}

Fields
------

{fields_section}
"""


# ── transform configuration sections ────────────────────────────────────────

def transform_configs_for(content):
    """Transform_v2 configs feeding this module, from its splunk
    ``normalize`` lists (``ecs_normalize/<path>.vrl`` ->
    ``transform_v2/<path>.yml``), deduplicated in reference order."""
    configs = []
    for params in (content.get("splunk") or {}).values():
        for path in (params or {}).get("normalize") or []:
            if not isinstance(path, str) or not path.startswith("ecs_normalize/"):
                continue
            rel = path[len("ecs_normalize/"):].rsplit(".", 1)[0] + ".yml"
            if rel not in configs and os.path.isfile(os.path.join(TRANSFORM_V2, rel)):
                configs.append(rel)
    return configs


def _literal(value):
    text = str(value).replace("`", "'")
    return f"``{text}``" if text else ""


def _spec_original(spec):
    """'Original' column of a set entry: source, operation call or literal."""
    if isinstance(spec, str):
        return spec
    if spec.get("value") is not None:
        value = spec["value"]
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            return "[" + ", ".join(str(v) for v in value) + "]"
        if isinstance(value, dict):
            return "{}"
        return f'"{value}"'
    source = spec.get("source")
    operation = spec.get("operation")
    if operation:
        return f"{operation}({source if source else ''})"
    return source or ""


def _anchor(anchor_prefix, kind, id_):
    """rst internal target name for a timeline ('tl') or relationship
    ('rel') id, unique per config to avoid collisions on multi-config pages."""
    safe = re.sub(r"[^a-zA-Z0-9-]", "-", str(id_))
    return f"{kind}-{anchor_prefix}-{safe}"


def _condition_value(entry, field):
    """Value of the condition on `field` in one timeline entry, if any."""
    for cond in entry.get("conditions") or []:
        if cond.get("field") == field and cond.get("value") is not None:
            return cond.get("value")
    return None


def _common_condition_fields(entries):
    """Condition fields present in EVERY timeline entry, in first-seen
    order. Fields shared by only part of the entries are ignored."""
    ordered = []
    common = None
    for entry in entries:
        fields = [
            cond.get("field")
            for cond in entry.get("conditions") or []
            if cond.get("field")
        ]
        field_set = set(fields)
        common = field_set if common is None else common & field_set
        for field in fields:
            if field not in ordered:
                ordered.append(field)
    if not common:
        return []
    return [field for field in ordered if field in common]


def timeline_rst(config_data, anchor_prefix=None, rel_ids=None):
    """Timeline table.

    Columns:
      - one column per condition field shared by EVERY timeline entry,
        holding the entry's condition value (no such column when no field
        is common to all entries)
      - 'Relation': the entry id, hyperlinked to the matching relationship
        of the same config when one exists
      - the message
    """
    entries = config_data.get("timeline") or []
    if not entries:
        return "No timeline messages."

    rel_ids = set(rel_ids or [])
    common_fields = _common_condition_fields(entries)

    lines = []
    if anchor_prefix:
        targets = []
        for entry in entries:
            if not entry.get("id"):
                continue
            # ids can repeat in a config: each anchor must be unique for reST
            target = f".. _{_anchor(anchor_prefix, 'tl', entry['id'])}:"
            if target not in targets:
                targets.append(target)
        if targets:
            lines += targets + [""]

    header = common_fields + ["Relation", "Message"]
    lines += [
        ".. list-table::",
        "   :header-rows: 1",
        "",
        "   * - " + "\n     - ".join(header),
    ]
    for entry in entries:
        cells = []
        for field in common_fields:
            value = _condition_value(entry, field)
            cells.append(_literal(value) if value is not None else "")
        entry_id = entry.get("id")
        if entry_id and entry_id in rel_ids:
            cells.append(
                f"`{rst_inline_safe(str(entry_id))} "
                f"<{_anchor(anchor_prefix, 'rel', entry_id)}_>`_"
            )
        else:
            cells.append(_literal(entry_id) if entry_id else "")
        cells.append(_literal(entry.get("message", "")))
        lines.append("   * - " + "\n     - ".join(cells))
    return "\n".join(lines)


def relationships_rst(config_data, anchor_prefix=None, tl_ids=None):
    """Relationships table: one row per relationship. The 'Relation' column
    holds the relationship id, hyperlinked back to the matching Timeline
    entry of the same config when one exists."""
    relationships = config_data.get("relationships") or []
    if not relationships:
        return "No relationships."

    tl_ids = set(tl_ids or [])

    lines = []
    if anchor_prefix:
        targets = []
        for rel in relationships:
            if not rel.get("id"):
                continue
            # ids can repeat in a config: each anchor must be unique for reST
            target = f".. _{_anchor(anchor_prefix, 'rel', rel['id'])}:"
            if target not in targets:
                targets.append(target)
        if targets:
            lines += targets + [""]

    lines += [
        ".. list-table::",
        "   :header-rows: 1",
        "",
        "   * - Relation",
        "     - Source",
        "     - Target",
        "     - Type",
    ]
    for rel in relationships:
        rel_id = rel.get("id")
        if rel_id and rel_id in tl_ids:
            relation = (
                f"`{rst_inline_safe(str(rel_id))} "
                f"<{_anchor(anchor_prefix, 'tl', rel_id)}_>`_"
            )
        else:
            relation = _literal(rel_id) if rel_id else ""
        lines.append(
            "   * - " + relation
            + "\n     - " + _literal(rel.get("source", ""))
            + "\n     - " + _literal(rel.get("target", ""))
            + "\n     - " + _literal(rel.get("type", ""))
        )
    return "\n".join(lines)


def fields_rst(config_data):
    """Field mappings of the transformation: original -> ECS field;
    custom blocks are not expanded, translate blocks are skipped."""
    rows = []
    for block in config_data.get("transformation") or []:
        if "set" in block:
            for target, spec in (block.get("set") or {}).items():
                rows.append((_spec_original(spec), target))
        elif "custom" in block:
            rows.append(("custom", ""))
    if not rows:
        return "No field mappings."
    lines = [
        ".. list-table::",
        "   :header-rows: 1",
        "",
        "   * - Original",
        "     - ECS field",
    ]
    for original, target in rows:
        lines.append(
            "   * - " + _literal(original)
            + "\n     - " + _literal(target)
        )
    return "\n".join(lines)


def _per_config(configs, render):
    """Render one section for each transform config; when a module uses
    several configs, each block is introduced by the config path."""
    if not configs:
        return "No transform configuration found for this module."
    blocks = []
    for rel in configs:
        with open(os.path.join(TRANSFORM_V2, rel), encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        part = render(data)
        if len(configs) > 1:
            part = f"**{_literal(rel)}**\n\n{part}"
        blocks.append(part)
    return "\n\n".join(blocks)


def rst_inline_safe(text):
    """Escape characters that reST would interpret as inline markup."""
    text = str(text)
    text = text.replace("\\", "\\\\")
    text = re.sub(r"\*", r"\\\*", text)
    text = text.replace("_", "\\_")
    text = text.replace("`", "'")
    return text


def rst_value(value):
    """Convert a YAML value to a short rst-friendly string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, list):
        return ", ".join(rst_value(v) for v in value)
    return rst_inline_safe(value)





def rst_literal(value):
    """Convert a YAML value to an rst inline literal."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(rst_literal(v) for v in value)
    return "``" + str(value).replace("`", "'") + "``"


def ingestion_tip(splunk):
    """Render the ingestion information as a 'tip' admonition: one line per
    sourcetype (sourcetype | name_rex), or a notice when the module does not
    ingest into Splunk."""
    if not splunk:
        return ".. tip:: The output of this module can't be ingested by splunk."

    lines = [
        ".. tip:: In Splunk you can find the result of the module after",
        "   ingestion with the following sourcetype:",
        "",
    ]
    for key, params in sorted(splunk.items()):
        params = params or {}
        sourcetype = params.get("sourcetype", key)
        name_rex = params.get("name_rex")
        if name_rex:
            lines.append(f"   * ``{sourcetype}`` | name_rex: ``{name_rex}``")
        else:
            lines.append(f"   * ``{sourcetype}``")
    return "\n".join(lines)


def _per_config_sections(configs):
    """Render the Timeline and Relationships sections for each transform
    config. Timeline entry ids and relationship ids cross-link within the
    same config; anchors are prefixed by the config path so multi-config
    pages don't collide."""
    if not configs:
        no_config = "No transform configuration found for this module."
        return no_config, no_config
    timeline_blocks = []
    relationship_blocks = []
    for rel in configs:
        with open(os.path.join(TRANSFORM_V2, rel), encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        anchor_prefix = os.path.splitext(rel)[0].replace(os.sep, "-")
        tl_ids = [
            entry.get("id")
            for entry in data.get("timeline") or []
            if entry.get("id")
        ]
        rel_ids = [
            rel_.get("id")
            for rel_ in data.get("relationships") or []
            if rel_.get("id")
        ]
        timeline = timeline_rst(data, anchor_prefix, rel_ids)
        relationships = relationships_rst(data, anchor_prefix, tl_ids)
        if len(configs) > 1:
            intro = f"**{_literal(rel)}**\n\n"
            timeline = intro + timeline
            relationships = intro + relationships
        timeline_blocks.append(timeline)
        relationship_blocks.append(relationships)
    return "\n\n".join(timeline_blocks), "\n\n".join(relationship_blocks)


def generate_module_page(yml_path, category, subcategory, module_info):
    with open(yml_path, encoding="utf-8") as fh:
        content = yaml.safe_load(fh) or {}

    metadata = content.get("metadata", {}) or {}

    title = os.path.splitext(os.path.basename(yml_path))[0]
    description = rst_inline_safe(metadata.get("description", ""))

    configs = transform_configs_for(content)
    timeline_section, relationships_section = _per_config_sections(configs)
    page = TEMPLATE.format(
        title=title,
        title_underline="=" * len(title),
        description=description,
        ingestion_tip=ingestion_tip(content.get("splunk", {}) or {}),
        timeline_section=timeline_section,
        relationships_section=relationships_section,
        fields_section=_per_config(configs, fields_rst),
    )

    rel = os.path.relpath(yml_path, MODULES_SRC)
    docname = os.path.splitext(rel)[0].replace(os.sep, "/")
    out_path = os.path.join(OUT_DIR, docname + ".rst")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(page)

    module_info[docname] = {
        "name": title,
        "description": str(metadata.get("description", "")),
        "category": category,
        "subcategory": subcategory,
    }
    return docname


SUBCATEGORY_TITLES = {
    "dfir-ogre": "DFIR-OGRE",
    "dissect": "Dissect",
    "live_response": "Live Response",
    "plasma": "Plasma",
    "registry": "Registry",
    "zimmerman": "Zimmerman",
}



def humanize(stem, subcategory=""):
    """Turn a module file stem into a readable card title.

    Known prefixes (ogre-, subcategory path) are stripped so that cards read
    e.g. "Acmru" instead of "Ogre Registry Acmru".
    """
    name = stem
    if name.startswith("ogre-"):
        name = name[len("ogre-"):]
    for part in subcategory.split("/") if subcategory else []:
        if name.startswith(part + "-"):
            name = name[len(part) + 1:]
    words = name.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


def card(href, title, description=""):
    """Return the HTML of one navigation card."""
    return (
        f'<a class="module-card" href="{html_mod.escape(href, quote=True)}">'
        f'<span class="module-card-title">{html_mod.escape(title)}</span>'
        f'<span class="module-card-desc">{html_mod.escape(description)}</span>'
        "</a>"
    )


def cards_grid(cards):
    """Return a 'raw:: html' block rendering the cards in a grid."""
    if not cards:
        return ""
    lines = [".. raw:: html", "", '   <div class="module-cards">']
    lines += ["   " + item for item in cards]
    lines += ["   </div>", ""]
    return "\n".join(lines)


def _write_page(path, title, intro, entries, cards_html=""):
    lines = [title, "=" * len(title), ""]
    if intro:
        lines += [intro, ""]
    if cards_html:
        lines += [cards_html]
    lines += [".. toctree::", "   :hidden:", ""]
    lines += [f"   {entry}" for entry in entries]
    lines.append("")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def generate_index(pages_by_location, module_info):
    """Write the Modules index pages: root, one per category and one per
    subcategory, so the sidebar navigation nests as
    Modules > Category > Subcategory > module pages. On every index page the
    content is rendered as a grid of navigation cards.

    pages_by_location: dict (category, subcategory) -> [docnames].
    module_info: dict docname -> {"name", "description", "category",
    "subcategory"}.
    """
    categories = sorted({category for category, _ in pages_by_location})

    # Root index: one card per category
    category_cards = []
    for category in categories:
        count = sum(
            len(docnames)
            for (cat, _), docnames in pages_by_location.items()
            if cat == category
        )
        category_cards.append(
            card(
                f"{category}/index.html",
                CATEGORY_TITLES.get(category, category.capitalize()),
                f"{count} module" if count == 1 else f"{count} modules",
            )
        )
    _write_page(
        os.path.join(OUT_DIR, "index.rst"),
        "Modules",
        "Each OSIR module is defined by a YAML configuration file located in\n"
        "``OSIR/configs/modules``. Modules are grouped by category and\n"
        "subcategory. Each module page is generated by ``modules_pages.py``.",
        [f"{category}/index" for category in categories],
        cards_grid(category_cards),
    )

    for category in categories:
        title = CATEGORY_TITLES.get(category, category.capitalize())
        subcategories = sorted(
            {sub for cat, sub in pages_by_location if cat == category and sub}
        )
        root_docnames = sorted(pages_by_location.get((category, ""), []))
        entries = [
            posixpath.relpath(docname, category) for docname in root_docnames
        ] + [f"{sub}/index" for sub in subcategories]

        sub_cards = [
            card(
                f"{subcategory}/index.html",
                SUBCATEGORY_TITLES.get(
                    subcategory, subcategory.replace("_", " ").capitalize()
                ),
                f"{len(pages_by_location[(category, subcategory)])} module"
                if len(pages_by_location[(category, subcategory)]) == 1
                else f"{len(pages_by_location[(category, subcategory)])} modules",
            )
            for subcategory in subcategories
        ]

        module_cards = [
            card(
                posixpath.relpath(docname, category) + ".html",
                humanize(module_info[docname]["name"]),
                module_info[docname]["description"],
            )
            for docname in root_docnames
        ]

        body = ""
        if sub_cards:
            body += "Subcategories\n-------------\n\n" + cards_grid(sub_cards) + "\n"
        if module_cards:
            body += "Modules\n-------\n\n" + cards_grid(module_cards) + "\n"
        _write_page(
            os.path.join(OUT_DIR, category, "index.rst"),
            title,
            f"Available modules for {title}.",
            entries,
            body,
        )

        for subcategory in subcategories:
            sub_title = f"{title} / {SUBCATEGORY_TITLES.get(subcategory, subcategory.replace('_', ' ').capitalize())}"
            docnames = sorted(pages_by_location[(category, subcategory)])
            entries = [
                posixpath.relpath(docname, f"{category}/{subcategory}")
                for docname in docnames
            ]
            cards = [
                card(
                    posixpath.relpath(docname, f"{category}/{subcategory}")
                    + ".html",
                    humanize(module_info[docname]["name"], subcategory),
                    module_info[docname]["description"],
                )
                for docname in docnames
            ]
            _write_page(
                os.path.join(OUT_DIR, category, subcategory, "index.rst"),
                sub_title,
                f"Available modules for {sub_title}.",
                entries,
                cards_grid(cards),
            )


def main():
    if not os.path.isdir(MODULES_SRC):
        raise SystemExit(f"Modules directory not found: {MODULES_SRC}")

    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    pages_by_location = {}
    module_info = {}
    count = 0
    for root, dirs, files in os.walk(MODULES_SRC):
        rel_root = os.path.relpath(root, MODULES_SRC)
        parts = [] if rel_root == "." else rel_root.split(os.sep)
        if parts and parts[0] in SKIP_CATEGORIES:
            continue
        category = parts[0] if parts else "common"
        # parts holds the directory components (no file name): a file under
        # <category>/<sub>/... belongs to subcategory <sub>; deeper levels are
        # flattened into the first-level subcategory.
        subcategory = parts[1] if len(parts) >= 2 else ""
        for file_name in sorted(files):
            if not file_name.endswith((".yml", ".yaml")):
                continue
            docname = generate_module_page(
                os.path.join(root, file_name), category, subcategory, module_info
            )
            pages_by_location.setdefault((category, subcategory), []).append(
                docname
            )
            count += 1

    generate_index(pages_by_location, module_info)
    print(f"Generated {count} module pages in {OUT_DIR}")


if __name__ == "__main__":
    main()
