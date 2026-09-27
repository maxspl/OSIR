journal_auth
============

.. tip:: Ingestion into Splunk.

   **``linux:journal_auth``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``journal_auth``
   * sourcetype: ``linux:journal_auth``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``journal_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``
   * artifact: ``journal_auth``

Description
-----------

Authentication events from the systemd journal (replaces auth.log on systemd-only hosts)

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
