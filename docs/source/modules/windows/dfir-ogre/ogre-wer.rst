ogre-wer
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:wer`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of wer - using ANSSI DFIR OGRE

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
   * - ``original_filename``
     - ``process.pe.original_file_name``
   * - ``application_identity``
     - ``process.entity_id``
   * - ``app_session_guid``
     - ``process.session_leader.id``
   * - ``boot_id``
     - ``host.boot.id``
   * - ``friendly_event_name``
     - ``event.reason``
   * - ``report_description``
     - ``message``
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``custom``
     - 
