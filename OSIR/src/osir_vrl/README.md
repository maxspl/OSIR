# osir_vrl — declarative VRL compiler

Compile YAML transformation configurations into Vector Remap Language
(VRL) programs. A configuration describes *what* to normalize; the package
generates the *how* — guards, error handling, cleanup — as a single `.vrl`
file. This wrapper is mainly use to know the structure of the parsed element and how to query them.

```
configs/dependencies/transform_v2/**.yml   --(OsirVrlModel.to_vrl)-->  *.vrl
```

Each config mirrors the path of the normalizer it drives:
`transform_v2/windows/amcache.yml` ↔ `ecs_normalize/windows/amcache.vrl`.

## Modules

| Module                    | Role                                                                                             |
|---------------------------|--------------------------------------------------------------------------------------------------|
| `OsirVrlModel`            | Root model: `metadata` + `source` + `transformation` + `timeline`; renders the full VRL program |
| `OsirVrlBlock`            | One item of `transformation`: a `set` / `translate` / `delete` / `custom` block, expanded into linear entries |
| `OsirVrlTransformation`   | One linear entry: renders its VRL lines (assignment, translation lookup, deletion, raw code) with its guard and error handling |
| `OsirVrlTimeline`         | Timeline entries: `message` + `relationships` + `conditions`                                     |
| `OsirVrlUtils`            | `extract_vrl_fields`, `render_value`, `condition_guard`                                          |

Public API: `OsirVrlModel.from_yaml(path)`, `.to_vrl()`, `.save_vrl(path)`,
`.entries` (flattened transformation entries).

## Configuration format

```yaml
metadata:
  version: "1.0"
  id: amcache                    # module id, used in generated log messages
  author: Typ
  type: PARSER & NORMALIZER      # optional, header only
  description: Windows Amcache CSV → ECS-ish generic normalizer

source:                          # optional, header only
  tools: amcache                 # collecting tool
  internal: amcache              # OSIR module name
  raw: raw                       # field holding the raw payload

transformation:                  # ordered list of blocks: first entry = first VRL instruction
  - set:
      event.kind:
        value: event             # literal value
      file.path: FullPath        # shorthand: plain source reference (field path or VRL expression)
      timestamp:
        source: raw              # explicit form
        operation: parse_timestamp
        parameters:
          format: "%Y-%m-%dT%H:%M:%SZ"
        on_error: log            # log (default for fallible ops) | direct
    filter: exists(.FullPath) && !exists(.file.path)   # optional block-level raw VRL guard
    conditions:                                         # optional block-level declarative guard
      - field: FullPath          # {field}          -> exists(.FullPath)
      - field: file.path
        exists: false            # {field, exists: false} -> !exists(.file.path)
      - field: event.kind
        value: event             # {field, value}   -> .event.kind == "event"

  - translate:
      mapping:
        action.name: event.id    # target -> source (one or more targets)
      dictionary:
        "4624": An account was successfully logged on
      fallback: Unknown event    # optional
    filter: .action.type == "Security"

  - delete:
      - Event                    # fields to del(), consecutive dels share one block
      - parsed_message_kv

  - custom: |-                   # raw VRL escape hatch
      if is_object(.json_data) {
        .event.outcome = "success"
      }

timeline:                        # rendered after the transformations, guarded per entry
  - message: "{user.name} logged on to {host.name}"
    relationships:
      - source: user.name
        target: host.name
        type: logged on to
    conditions:
      - field: event.id
        value: 4624
```

### Conventions

- **No comments** in the configuration files: the description of the file
  lives in `metadata.description`, everything else is structure.
- **No `fields` section**: field documentation is not part of the package.
- **Sources are written without a leading dot** (`Event.System.TimeCreated`,
  not `.Event.System.TimeCreated`). The model accepts both and always
  renders `.path`.

### Block semantics

- `transformation` is a **linear program**: blocks render in list order,
  entries within a block in mapping order. Order is semantics — a later
  block sees the fields set by an earlier one.
- A block takes **exactly one** kind (`set` / `translate` / `delete` /
  `custom`); anything else is a validation error.
- `filter` (raw VRL) and `conditions` (declarative) sit **at the block
  level**, next to the kind key, and guard **every entry** of the block.
  They never appear inside an entry.

### `set` entries

Two forms, per target:

1. shorthand — `target: <source string>`: a dotted field path or a VRL
   expression used as source;
2. mapping — `target: {source | value | operation | parameters | on_error}`:
   `value` for a literal (string, number, boolean, list, `{}`), `source`
   with `operation` + `parameters` for a function call.

Rendering rules:

- a **plain path source** is guarded by `if exists(.src) { ... }`;
- a **source expression** is guarded by `exists()` on every field it
  references (`extract_vrl_fields`);
- a **value** gets no default guard;
- an `operation` on a fallible function is rendered with a non-aborting
  error handler (`_result, err = ...` + warn log); a bang variant
  (`downcase!`) or `on_error: direct` renders verbatim; infallible
  operations (`now`, `uuid_v4`, `encode_json`) render as direct calls;
- **guard dedup**: a default `exists(.src)` is omitted when the block
  filter/conditions already contain a *positive* `exists(.src)` —
  `!exists(.src)` does not count.

### `translate` blocks (v1 structure)

`mapping: {target: source}` + a shared `dictionary` + optional `fallback`.
Rendered as `get(value: {...}, path: [to_string!(.source)]) ?? "fallback"`
(with the same error-handler pattern as sets when there is no fallback).
Dictionary keys load as YAML scalars — numeric keys (`"4624"`) are coerced
to strings automatically, but quoting them is the convention.

### `delete` blocks

A list of field names, rendered as one `del(.field)` per field, each
independent (no combined guard). Optional block-level `filter`/`conditions`
wrap the whole group.

### `custom` blocks

Raw VRL, rendered verbatim inside the optional block-level guard. Use it
for control flow (if/else chains, intermediate variables), and anything
the other blocks cannot express. A custom block must not declare a
`set`/`translate`/`delete` key.

### Flat dotted keys ("normalize dotted fields")

When a **source expression or a filter** references a *dotted* field
(`to_int!(.Event.System.EventID)`, `!exists(.file.path)`), the model
assumes the raw event may hold it as a single flat key
(`"Event.System.EventID"`) and prepends a normalization section:

```vrl
if exists(."Event.System.EventID") { .Event.System.EventID = get!(., path: ["Event.System.EventID"]) }
```

This is intended for flattened inputs (XML/JSONL). It never triggers for
`conditions` (they reference real event paths), plain-path sources, or
`custom` blocks.

### Timeline

Rendered after all transformations, one block per entry, guarded by its
conditions plus `exists()` on every `{field}` referenced in the message
template. Entries are sorted by number of conditions (most specific
first). `relationships` are pushed into `.relationships` as
`{source, target, type}` objects.

## Generating and verifying

```bash
# compile one config to VRL
python3 -c "import sys; sys.path.insert(0, 'src'); \
  from osir_vrl.osir_vrl.OsirVrlModel import OsirVrlModel; \
  OsirVrlModel.from_yaml('configs/dependencies/transform_v2/linux/mactime.yml').save_vrl('/tmp/out.vrl')"

# verify: every config loads, generates, and its VRL compiles with vector
cd OSIR && python3 -m pytest tests/test_transform_v2.py -q

# full suite (OSIR_PATH must be set for test_modules)
python3 -m pytest tests/ -q

# compile check by hand
vector vrl -p /tmp/out.vrl -i event.json -o
```

`tests/test_transform_v2.py` walks every `transform_v2/**/*.yml`, asserts
each generates a VRL that compiles with the `vector` CLI (skipped when
vector is absent), and fails loudly on legacy formats (`pipeline`/`stages`
or the flat pre-block `transformations` list).
