ogre-registry-scheduled-task
============================

.. tip:: Ingestion into Splunk.

   **``windows:ogre:registry_scheduled_task``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-registry-scheduled-task``
   * sourcetype: ``windows:ogre:registry_scheduled_task``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``hive``
   * timestamp_path: ``creation_date``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of scheduled\_tasks - using ANSSI DFIR OGRE

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
