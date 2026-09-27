last
====

.. tip:: Ingestion into Splunk.

   **``linux:live_response:system:last``**

   * name_rex: ``last.*\.jsonl$``
   * path_suffix: ``system``
   * sourcetype: ``linux:live_response:system:last``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``login``
   * timestamp_format: ``%a %b %d %H:%M``
   * artifact: ``last``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command last and lastb

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
