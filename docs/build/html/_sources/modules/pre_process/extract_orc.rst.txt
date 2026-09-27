extract_orc
===========

.. tip:: Ingestion into Splunk.

   **``filesystem:ntfs:i30``**

   * name_rex: ``I30Info.*.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * sourcetype: ``filesystem:ntfs:i30``
   * host_rex: ``/Endpoint_(.*?)/``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * encoding: ``utf-8``
   * normalize: ``ecs_normalize/windows/NTFSInfo_i30.vrl``

   **``filesystem:ntfs:info``**

   * name_rex: ``NTFSInfo.*.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * sourcetype: ``filesystem:ntfs:info``
   * host_rex: ``/Endpoint_(.*?)/``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * encoding: ``utf-8``
   * normalize: ``ecs_normalize/windows/NTFSInfo.vrl``

   **``filesystem:ntfs:usn``**

   * name_rex: ``USNInfo.*.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * sourcetype: ``filesystem:ntfs:usn``
   * host_rex: ``/Endpoint_(.*?)/``
   * timestamp_path: ``TimeStamp``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S.%f``

   **``orc:collected_files``**

   * name_rex: ``GetThis.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * sourcetype: ``orc:collected_files``
   * host_rex: ``/Endpoint_(.*?)/``
   * timestamp_path: ``CreationDate``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S.%f``

   **``orc:csv``**

   * name_rex: ``\.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * sourcetype: ``orc:files``
   * host_rex: ``/Endpoint_(.*?)/``
   * artifact: ``Orc``

   **``windows:live_response:autoruns``**

   * name_rex: ``autoruns.*csv$``
   * path_rex: ``.*\/extract_orc.*``
   * sourcetype: ``windows:autoruns``
   * host_rex: ``/Endpoint_(.*?)/``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/windows/live_response/autoruns.vrl``

   **``windows:live_response:processes``**

   * name_rex: ``(?i)(?:^|/)processes(?:\d+|_[^/]+)?\.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * host_rex: ``/Endpoint_(.*?)/``
   * sourcetype: ``_json``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/windows/live_response/ps1_processes.vrl``

   **``windows:live_response:systeminfo``**

   * name_rex: ``(?i)^systeminfo(?:_.+)?\.csv$``
   * path_rex: ``.*\/extract_orc.*``
   * host_rex: ``/Endpoint_(.*?)/``
   * sourcetype: ``_json``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/windows/live_response/systeminfo.vrl``

Description
-----------

Used to execute internal pre-processing for DFIR-ORC capture

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
