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

Placeholder table for the messages created for the timeline.

.. list-table::
   :header-rows: 1

   * - Timeline
     - ECS field
     - Message
   * -
     -
     -

Fields
------

Placeholder table for the output fields.

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * -
     -
"""


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
    """Render the ingestion information as a 'tip' admonition."""
    if not splunk:
        return (".. tip:: This module does not ingest data into Splunk.")

    lines = [".. tip:: Ingestion into Splunk.", ""]
    for key, params in sorted(splunk.items()):
        lines += [f"   **``{key}``**", ""]
        for name, value in params.items():
            lines += [f"   * {name}: {rst_literal(value)}"]
        lines.append("")
    return "\n".join(lines).rstrip()


def generate_module_page(yml_path, category, subcategory, module_info):
    with open(yml_path, encoding="utf-8") as fh:
        content = yaml.safe_load(fh) or {}

    metadata = content.get("metadata", {}) or {}

    title = os.path.splitext(os.path.basename(yml_path))[0]
    description = rst_inline_safe(metadata.get("description", ""))

    page = TEMPLATE.format(
        title=title,
        title_underline="=" * len(title),
        description=description,
        ingestion_tip=ingestion_tip(content.get("splunk", {}) or {}),
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
