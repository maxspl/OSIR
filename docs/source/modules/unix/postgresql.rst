postgresql
==========

.. tip:: Ingestion into Splunk.

   **``linux:postgres``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``postgresql``
   * sourcetype: ``linux:postgres``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%s``
   * artifact: ``postgres``

Description
-----------

Parsing logs from '/var/log/postgresql'

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
