yum
===

.. tip:: Ingestion into Splunk.

   **``linux:yum``**

   * name_rex: ``yum.*\.jsonl$``
   * sourcetype: ``linux:yum``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S``
   * artifact: ``yum``

Description
-----------

Parsing logs from '/var/log/yum'

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
