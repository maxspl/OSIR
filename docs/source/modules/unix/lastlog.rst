lastlog
=======

.. tip:: Ingestion into Splunk.

   **``linux:lastlog``**

   * name_rex: ``lastlog.*\.jsonl$``
   * sourcetype: ``linux:lastlog``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S%z``
   * artifact: ``lastlog``

Description
-----------

Parsing logs from '/var/log/lastlog'

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
