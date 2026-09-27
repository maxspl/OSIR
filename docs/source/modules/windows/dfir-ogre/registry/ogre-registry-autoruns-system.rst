ogre-registry-autoruns-system
=============================

.. tip:: Ingestion into Splunk.

   **``windows:ogre:registry_autoruns_system``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-registry-autoruns-system``
   * sourcetype: ``windows:ogre:registry_autoruns_system``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``hive``
   * timestamp_path: ``key_modif_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of autorun\_hive - using ANSSI DFIR OGRE

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
