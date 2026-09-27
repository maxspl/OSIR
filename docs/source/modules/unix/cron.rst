cron
====

.. tip:: Ingestion into Splunk.

   **``linux:cron``**

   * name_rex: ``cron.*\.jsonl$``
   * sourcetype: ``linux:cron``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S``
   * artifact: ``cron``

Description
-----------

Parsing logs from '/var/log/cron'

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
