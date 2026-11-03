wer
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:wer`` | name_rex: ``r"--wer\.jsonl$"``

Description
-----------

Parse .wer files

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
   * - ``"Windows Error Reporting (WER)"``
     - ``event.provider``
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``OriginalFilename``
     - ``process.pe.original_file_name``
   * - ``ApplicationIdentity``
     - ``process.entity_id``
   * - ``AppSessionGuid``
     - ``process.session_leader.id``
   * - ``BootId``
     - ``host.boot.id``
   * - ``FriendlyEventName``
     - ``event.reason``
   * - ``ReportDescription``
     - ``message``
   * - ``_file``
     - ``log.file.path``
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``custom``
     - 
