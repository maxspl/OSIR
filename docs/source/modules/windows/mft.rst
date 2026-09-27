mft
===

.. tip:: Ingestion into Splunk.

   **``filesystem:ntfs:info``**

   * name_rex: ``\$MFT.*\.csv$``
   * sourcetype: ``filesystem:ntfs:info``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S%.f``
   * artifact: ``mft``
   * normalize: ``ecs_normalize/windows/mft.vrl``

   **``filesystem:ntfs:usn``**

   * name_rex: ``\$J.*.csv$``
   * sourcetype: ``filesystem:ntfs:usn``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S.%f``
   * normalize: ``ecs_normalize/windows/usn.vrl``

Description
-----------

Parsing of $MFT artifact.

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
