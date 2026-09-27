syslog
======

.. tip:: Ingestion into Splunk.

   **``linux:syslog``**

   * name_rex: ``syslog.*\.jsonl$``
   * sourcetype: ``linux:syslog``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S``
   * artifact: ``syslog``

Description
-----------

Parsing logs from '/var/log/syslog'

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
