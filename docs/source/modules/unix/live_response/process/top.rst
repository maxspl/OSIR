top
===

.. tip:: Ingestion into Splunk.

   **``linux:live_response:top``**

   * name_rex: ``top.*\.jsonl$``
   * path_suffix: ``process``
   * sourcetype: ``linux:live_response:top``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``time``
   * timestamp_format: ``%H:%M:%S``
   * artifact: ``top``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command top and top -b

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
