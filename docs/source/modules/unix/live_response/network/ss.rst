ss
==

.. tip:: Ingestion into Splunk.

   **``linux:live_response:network:ss``**

   * name_rex: ``ss.*\.jsonl$``
   * path_suffix: ``network``
   * sourcetype: ``linux:live_response:network:ss``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``ss``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command ss. UAC collects ss rather than netstat on modern distributions.

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
