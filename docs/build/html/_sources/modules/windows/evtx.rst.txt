evtx
====

.. tip:: Ingestion into Splunk.

   **``windows:evtx``**

   * name_rex: ``\.evtx.*\.jsonl$``
   * path_suffix: ``evtx``
   * sourcetype: ``windows:evtx``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/evtx.vrl``

   **``windows:evtx:powershell``**

   * name_rex: ``PowerShell\.evtx.*\.jsonl$``
   * path_suffix: ``evtx``
   * sourcetype: ``windows:evtx:powershell``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/evtx.vrl``

   **``windows:evtx:powershell:operational``**

   * name_rex: ``PowerShell.*Operational\.evtx.*\.jsonl$``
   * path_suffix: ``evtx``
   * sourcetype: ``windows:evtx:powershell:operational``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/evtx.vrl``

   **``windows:evtx:security``**

   * name_rex: ``Security\.evtx.*\.jsonl$``
   * path_suffix: ``evtx``
   * sourcetype: ``windows:evtx:security``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/evtx.vrl``

   **``windows:evtx:sysmon``**

   * name_rex: ``Sysmon.*\.evtx.*\.jsonl$``
   * path_suffix: ``evtx``
   * sourcetype: ``windows:evtx:sysmon``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/evtx.vrl``

   **``windows:evtx:system``**

   * name_rex: ``System\.evtx.*\.jsonl$``
   * path_suffix: ``evtx``
   * sourcetype: ``windows:evtx:system``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/evtx.vrl``

Description
-----------

Parsing of EVTX collected by DFIR ORC or in the filesystem

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
