mongodb
=======

.. tip:: Ingestion into Splunk.

   **``linux:app:mongodb``**

   * name_rex: ``mongod.log$``
   * sourcetype: ``linux:app:mongodb``
   * host_rex: ``extract_uac/(.*?)/``
   * artifact: ``mongodb``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * normalize: ``ecs_normalize/linux/mongodb.vrl``

Description
-----------

Splunk logs ingestion of Mongodb logs.

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
