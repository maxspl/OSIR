zeek_log
========

.. tip:: Ingestion into Splunk.

   **``linux:network:zeek``**

   * name_rex: ``\.jsonl$``
   * sourcetype: ``linux:network:zeek``
   * host_rex: ``/Endpoint_(.*?)/``
   * timestamp_path: ``_time``
   * timestamp_format: ``%s``
   * artifact: ``audit``

Description
-----------

Parsing logs from Zeek

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
