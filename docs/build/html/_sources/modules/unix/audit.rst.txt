audit
=====

.. tip:: Ingestion into Splunk.

   **``linux:audit``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``audit``
   * sourcetype: ``linux:audit``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%s``
   * artifact: ``audit``

Description
-----------

Parsing logs from '/var/log/audit'

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
