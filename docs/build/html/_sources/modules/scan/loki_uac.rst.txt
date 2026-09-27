loki_uac
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``loki:files`` | name_rex: ``\.jsonl$``

Description
-----------

YARA/IOC scan of the files collected by UAC (output of the extract\_uac module) using Loki-RS.

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
   * - ``"loki"``
     - ``event.module``
   * - ``"Nextron Systems"``
     - ``observer.vendor``
   * - ``"Loki-RS"``
     - ``observer.product``
   * - ``"scanner"``
     - ``observer.type``
   * - ``custom``
     - 
   * - ``to_string(.message) ?? null``
     - ``message``
   * - ``custom``
     - 
   * - ``to_string(.file_type) ?? null``
     - ``file.type``
   * - ``custom``
     - 
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
   * - ``custom``
     - 
   * - ``to_string(.process_name) ?? null``
     - ``process.name``
   * - ``custom``
     - 
   * - ``to_string(.run_time) ?? null``
     - ``loki.process.run_time``
   * - ``custom``
     - 
   * - ``listening_ports``
     - ``loki.process.listening_ports``
   * - ``custom``
     - 
   * - ``context``
     - ``loki.context``
