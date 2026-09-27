lnk
===

.. tip:: Ingestion into Splunk.

   **``windows:lnk``**

   * name_rex: ``\.csv$``
   * path_suffix: ``lnk``
   * sourcetype: ``windows:files:lnk``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``Lnk``
   * normalize: ``ecs_normalize/windows/lnk.vrl``

Description
-----------

Parsing of lnk artifact.

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
