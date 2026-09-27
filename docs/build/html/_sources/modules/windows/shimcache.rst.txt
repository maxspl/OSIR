shimcache
=========

.. tip:: Ingestion into Splunk.

   **``windows:shimcache``**

   * name_rex: ``\.csv$``
   * path_suffix: ``shimcache``
   * sourcetype: ``windows:registry:hklm:shimcache``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``ShimCache``
   * normalize: ``ecs_normalize/windows/shimcache.vrl``

Description
-----------

Parsing of ShimCache artifact.

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
