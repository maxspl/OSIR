hives_hklm
==========

.. tip:: Ingestion into Splunk.

   **``windows:hklm``**

   * name_rex: ``--hives_*\w*\.csv``
   * path_rex: ``.*\/hives_hklm.*``
   * sourcetype: ``windows:registry:hklm``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``Hives``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/windows/hives.vrl``

Description
-----------

Parsing of registry hives artifact.

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
