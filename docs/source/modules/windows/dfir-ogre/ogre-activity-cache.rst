ogre-activity-cache
===================

.. tip:: Ingestion into Splunk.

   **``windows:ogre:activity_cache``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-activity-cache``
   * sourcetype: ``windows:ogre:activity_cache``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``Activity Cache``
   * timestamp_path: ``start_time``, ``last_modified_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of activity\_cache - using ANSSI DFIR OGRE

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
