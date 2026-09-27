amcache
=======

.. tip:: Ingestion into Splunk.

   **``windows:amcache``**

   * name_rex: ``\.csv$``
   * path_suffix: ``amcache``
   * sourcetype: ``windows:files:amcache``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``AmCache``
   * normalize: ``ecs_normalize/windows/amcache.vrl``

Description
-----------

Parsing of amcache artifact.

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
