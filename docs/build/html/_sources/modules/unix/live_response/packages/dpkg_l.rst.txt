dpkg_l
======

.. tip:: Ingestion into Splunk.

   **``linux:live_response:packages:dpkg``**

   * name_rex: ``dpkg.*\.jsonl$``
   * sourcetype: ``linux:live_response:packages:dpkg``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``dpkg``
   * normalize: ``ecs_normalize/linux/live_response/packages/dpkg.vrl``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command dpkg -l

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
