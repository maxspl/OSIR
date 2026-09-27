shell_bags
==========

.. tip:: Ingestion into Splunk.

   **``windows:shellbags``**

   * name_rex: ``\.csv$``
   * path_suffix: ``shell_bags``
   * sourcetype: ``windows:registry:hku:shellbags``
   * host_rex: ``([\w\.-]+?)--shell_bags\.csv$``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``ShellBags``
   * normalize: ``ecs_normalize/windows/shell_bags.vrl``

Description
-----------

Parsing of shell bags artifact.

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
