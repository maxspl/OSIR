auth
====

.. tip:: Ingestion into Splunk.

   **``linux:auth``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``auth``
   * sourcetype: ``linux:auth``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S``
   * artifact: ``auth``

Description
-----------

Parsing logs from '/var/log/auth.log'

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
