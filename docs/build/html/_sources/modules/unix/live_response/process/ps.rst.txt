ps
==

.. tip:: Ingestion into Splunk.

   **``linux:live_response:ps``**

   * name_rex: ``ps.*\.jsonl$``
   * path_suffix: ``process``
   * sourcetype: ``linux:live_response:process:ps``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``ps``

Description
-----------

Kelly Brazil - JsonConverter - Parsing the output of the command ps and ps -ef

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
