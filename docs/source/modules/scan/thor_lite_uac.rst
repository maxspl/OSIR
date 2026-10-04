thor_lite_uac
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``thor:files`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Scan of collected file using Thor Lite.

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
   * - ``"alert"``
     - ``event.kind``
   * - ``"thor"``
     - ``event.module``
   * - ``"Nextron THOR"``
     - ``event.provider``
   * - ``"Nextron Systems"``
     - ``observer.vendor``
   * - ``"THOR"``
     - ``observer.product``
   * - ``"scanner"``
     - ``observer.type``
   * - ``to_string(.time) ?? null``
     - ``timestamp``
   * - ``to_string(.time) ?? null``
     - ``event.created``
   * - ``.timestamp``
     - ``event.created``
   * - ``to_string(.event_time) ?? null``
     - ``timestamp``
   * - ``to_string(.hostname) ?? null``
     - ``observer.hostname``
   * - ``to_string(.event_computer) ?? null``
     - ``host.name``
   * - ``to_string(.event_computer) ?? null``
     - ``winlog.computer_name``
   * - ``to_string(.hostname) ?? null``
     - ``host.name``
   * - ``to_string(.level) ?? null``
     - ``log.level``
   * - ``"thor." + downcase!(to_string!(.module))``
     - ``event.dataset``
   * - ``to_string!(.module)``
     - ``log.logger``
   * - ``"thor"``
     - ``event.dataset``
   * - ``to_string(.message) ?? null``
     - ``message``
   * - ``to_string(.scanid) ?? null``
     - ``thor.scan.id``
   * - ``to_string(.log_version) ?? null``
     - ``observer.version``
   * - ``to_string(.log_version) ?? null``
     - ``thor.log.version``
   * - ``to_int(.score) ?? null``
     - ``event.risk_score``
   * - ``to_int(.score) ?? null``
     - ``event.severity``
   * - ``to_int(.score) ?? null``
     - ``thor.score``
   * - ``to_int(.subscore_1) ?? null``
     - ``rule.risk_score``
   * - ``to_int(.subscore_1) ?? null``
     - ``thor.primary.subscore``
   * - ``to_string(.reason_1) ?? null``
     - ``event.reason``
   * - ``to_string(.reason_1) ?? null``
     - ``thor.primary.reason``
   * - ``to_string(.rulename_1) ?? null``
     - ``rule.name``
   * - ``to_string(.reason_1) ?? null``
     - ``rule.name``
   * - ``to_string(.id_1) ?? null``
     - ``rule.id``
   * - ``to_string(.description_1) ?? null``
     - ``rule.description``
   * - ``[to_string!(.author_1)]``
     - ``rule.author``
   * - ``to_string(.ref_1) ?? null``
     - ``rule.reference``
   * - ``to_string(.ruledate_1) ?? null``
     - ``rule.created``
   * - ``to_string(.sigtype_1) ?? null``
     - ``rule.ruleset``
   * - ``to_string(.sigtype_1) ?? null``
     - ``thor.primary.signature.type``
   * - ``to_string(.sigclass_1) ?? null``
     - ``rule.category``
   * - ``to_string(.sigclass_1) ?? null``
     - ``thor.primary.signature.class``
   * - ``to_string(.falsepositives_1) ?? null``
     - ``thor.primary.false_positives``
   * - ``split!(to_string!(.tags_1), ",")``
     - ``rule.tags``
   * - ``to_string!(.tags_1)``
     - ``thor.primary.tags``
   * - ``matched_1``
     - ``thor.primary.matched``
   * - ``to_int(.reasons_count) ?? null``
     - ``thor.reasons_count``
   * - ``downcase!(to_string!(.module))``
     - ``module_lower``
   * - ``[file, malware]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"thor-filescan-match"``
     - ``event.action``
   * - ``[file, malware]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"thor-logscan-match"``
     - ``event.action``
   * - ``[malware]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"thor-evtx-match"``
     - ``event.action``
   * - ``[malware]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"thor-match"``
     - ``event.action``
   * - ``to_string(.file) ?? null``
     - ``thor_file_path``
   * - ``thor_file_path``
     - ``file.path``
   * - ``basename!(.thor_file_path)``
     - ``file.name``
   * - ``to_string(.file_1) ?? null``
     - ``thor.primary.file.path``
   * - ``to_string(.file_1) ?? null``
     - ``file.path``
   * - ``basename!(to_string!(.file_1))``
     - ``file.name``
   * - ``to_string(.exists_1) ?? null``
     - ``thor.primary.file.exists``
   * - ``replace(to_string!(.ext), ".", "")``
     - ``file.extension``
   * - ``to_string(.type) ?? null``
     - ``file.type``
   * - ``to_string(.type_1) ?? null``
     - ``file.type``
   * - ``to_int(.size) ?? null``
     - ``file.size``
   * - ``to_int(.size_1) ?? null``
     - ``file.size``
   * - ``to_string(.md5) ?? null``
     - ``file.hash.md5``
   * - ``to_string(.md5_1) ?? null``
     - ``file.hash.md5``
   * - ``to_string(.sha1) ?? null``
     - ``file.hash.sha1``
   * - ``to_string(.sha1_1) ?? null``
     - ``file.hash.sha1``
   * - ``to_string(.sha256) ?? null``
     - ``file.hash.sha256``
   * - ``to_string(.sha256_1) ?? null``
     - ``file.hash.sha256``
   * - ``to_string(.permissions) ?? null``
     - ``file.mode``
   * - ``to_string(.permissions_1) ?? null``
     - ``file.mode``
   * - ``to_string(.owner) ?? null``
     - ``file.owner``
   * - ``to_string(.owner_1) ?? null``
     - ``file.owner``
   * - ``to_string(.group) ?? null``
     - ``file.group``
   * - ``to_string(.group_1) ?? null``
     - ``file.group``
   * - ``to_string(.firstbytes) ?? null``
     - ``thor.file.first_bytes``
   * - ``to_string(.firstbytes_1) ?? null``
     - ``thor.file.first_bytes``
   * - ``to_int(.event_id) ?? null``
     - ``winlog.event_id``
   * - ``to_string!(to_int!(.event_id))``
     - ``event.code``
   * - ``to_string(.event_id) ?? null``
     - ``event.code``
   * - ``to_string(.event_level) ?? null``
     - ``winlog.level``
   * - ``to_string(.event_channel) ?? null``
     - ``winlog.channel``
   * - ``to_string(.entry) ?? .entry``
     - ``thor.entry``
   * - ``to_string(.log_modified) ?? null``
     - ``thor.log.modified``
   * - ``to_string(.log_accessed) ?? null``
     - ``thor.log.accessed``
