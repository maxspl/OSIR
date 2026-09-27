ogre-chrome-history
===================

.. tip:: Ingestion into Splunk.

   **``windows:ogre:chrome_history``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-chrome-history``
   * sourcetype: ``windows:ogre:chrome_history``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``chrome``
   * timestamp_path: ``visit_date``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of browser\_history - using ANSSI DFIR OGRE

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
