loki_orc
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``loki:files`` | name_rex: ``r"\.jsonl$"``

Description
-----------

YARA/IOC scan of the filesystem rebuilt from a DFIR ORC collection (output of the restore\_fs module) using Loki-RS.

Timeline
--------

No timeline messages.

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"loki"``
     - ``event.module``
   * - ``"Nextron Systems"``
     - ``observer.vendor``
   * - ``"Loki-RS"``
     - ``observer.product``
   * - ``"scanner"``
     - ``observer.type``
   * - ``format_timestamp!(parse_timestamp!(to_string!(.timestamp), format: "%+"), format: "%Y-%m-%dT%H:%M:%SZ")``
     - ``timestamp``
   * - ``to_string!(.hostname)``
     - ``observer.hostname``
   * - ``downcase!(to_string!(.level))``
     - ``log.level``
   * - ``"90"``
     - ``event.severity``
   * - ``"70"``
     - ``event.severity``
   * - ``"50"``
     - ``event.severity``
   * - ``"40"``
     - ``event.severity``
   * - ``"10"``
     - ``event.severity``
   * - ``to_string(.message) ?? null``
     - ``message``
   * - ``to_int(to_float(.score) ?? 0.0)``
     - ``event.risk_score``
   * - ``to_int(to_float(.score) ?? 0.0)``
     - ``loki.score``
   * - ``downcase(to_string(.event_type) ?? "info")``
     - ``event_type_lower``
   * - ``"alert"``
     - ``event.kind``
   * - ``[file, malware]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"loki-file-match"``
     - ``event.action``
   * - ``"loki.filescan"``
     - ``event.dataset``
   * - ``"alert"``
     - ``event.kind``
   * - ``[process, malware]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"loki-process-match"``
     - ``event.action``
   * - ``"loki.processcheck"``
     - ``event.dataset``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[start]``
     - ``event.type``
   * - ``"loki-scan-start"``
     - ``event.action``
   * - ``"loki.scan"``
     - ``event.dataset``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[end]``
     - ``event.type``
   * - ``"loki-scan-end"``
     - ``event.action``
   * - ``"loki.scan"``
     - ``event.dataset``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[error]``
     - ``event.type``
   * - ``"loki-scan-error"``
     - ``event.action``
   * - ``"loki.scan"``
     - ``event.dataset``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"loki-scan-info"``
     - ``event.action``
   * - ``"loki.scan"``
     - ``event.dataset``
   * - ``to_string(.file_path) ?? null``
     - ``file.path``
   * - ``basename!(to_string!(.file_path))``
     - ``file.name``
   * - ``downcase!(to_string!(split(basename!(to_string!(.file_path)), ".")[-1]))``
     - ``file.extension``
   * - ``to_string(.file_type) ?? null``
     - ``file.type``
   * - ``to_int(.file_size) ?? null``
     - ``file.size``
   * - ``to_string(.md5) ?? null``
     - ``file.hash.md5``
   * - ``to_string(.sha1) ?? null``
     - ``file.hash.sha1``
   * - ``to_string(.sha256) ?? null``
     - ``file.hash.sha256``
   * - ``to_string(.file_created) ?? null``
     - ``file.created``
   * - ``to_string(.file_modified) ?? null``
     - ``file.mtime``
   * - ``to_string(.file_accessed) ?? null``
     - ``file.accessed``
   * - ``to_int(.pid) ?? null``
     - ``process.pid``
   * - ``to_string(.process_name) ?? null``
     - ``process.name``
   * - ``format_timestamp!(from_unix_timestamp!(to_int!(.start_time)), format: "%Y-%m-%dT%H:%M:%SZ")``
     - ``process.start``
   * - ``to_string(.run_time) ?? null``
     - ``loki.process.run_time``
   * - ``to_int(.memory_bytes) ?? null``
     - ``loki.process.memory_bytes``
   * - ``to_float(.cpu_usage) ?? null``
     - ``loki.process.cpu_usage``
   * - ``to_int(.connection_count) ?? null``
     - ``loki.process.connection_count``
   * - ``listening_ports``
     - ``loki.process.listening_ports``
   * - ``custom``
     - 
   * - ``context``
     - ``loki.context``
