journal_cron
============

.. tip:: Ingestion into Splunk.

   **``linux:journal_cron``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``journal_cron``
   * sourcetype: ``linux:journal_cron``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``journal_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``
   * artifact: ``journal_cron``

Description
-----------

Cron events from the systemd journal

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
