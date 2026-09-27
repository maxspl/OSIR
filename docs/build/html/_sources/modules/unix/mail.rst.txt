mail
====

.. tip:: Ingestion into Splunk.

   **``linux:mail``**

   * name_rex: ``mail.*\.jsonl$``
   * sourcetype: ``linux:mail``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S``
   * artifact: ``mail``

Description
-----------

Parsing logs from '/var/log/mail'

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
