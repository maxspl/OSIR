who
===

.. tip:: Ingestion into Splunk.

   **``linux:live_response:system:who``**

   * name_rex: ``who.*\.jsonl$``
   * path_suffix: ``system``
   * sourcetype: ``linux:live_response:system:who``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``epoch``
   * timestamp_format: ``%s``
   * artifact: ``who``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command who. UAC collects who rather than last on modern distributions.

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
