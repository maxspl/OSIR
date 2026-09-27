thor_uac
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``thor:files`` | name_rex: ``\.jsonl$``

Description
-----------

Scan of collected UAC (output of extract\_uac module) files using Thor (requires Forensic license).

Timeline
--------

No timeline messages.

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
   * - ``custom``
     - 
   * - ``to_string(.level) ?? null``
     - ``log.level``
   * - ``custom``
     - 
   * - ``to_string(.message) ?? null``
     - ``message``
   * - ``to_string(.scanid) ?? null``
     - ``thor.scan.id``
   * - ``custom``
     - 
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
   * - ``custom``
     - 
   * - ``to_string(.falsepositives_1) ?? null``
     - ``thor.primary.false_positives``
   * - ``custom``
     - 
   * - ``matched_1``
     - ``thor.primary.matched``
   * - ``custom``
     - 
   * - ``to_string(.exists_1) ?? null``
     - ``thor.primary.file.exists``
   * - ``custom``
     - 
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
