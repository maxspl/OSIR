dpkg
====

.. tip:: Ingestion into Splunk.

   **``linux:dpkg``**

   * name_rex: ``dpkg.*\.jsonl$``
   * sourcetype: ``linux:dpkg``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S``
   * artifact: ``dpkg``

Description
-----------

Parsing logs from '/var/log/dpkg'

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
