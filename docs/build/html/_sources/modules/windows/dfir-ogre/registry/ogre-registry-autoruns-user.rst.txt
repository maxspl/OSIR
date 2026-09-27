ogre-registry-autoruns-user
===========================

.. tip:: Ingestion into Splunk.

   **``windows:ogre:registry_autoruns_user``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-registry-autoruns-user``
   * sourcetype: ``windows:ogre:registry_autoruns_user``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``hive``
   * timestamp_path: ``key_modif_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of reg\_autoruns - using ANSSI DFIR OGRE

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
