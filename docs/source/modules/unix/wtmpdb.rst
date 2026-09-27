wtmpdb
======

.. tip:: Ingestion into Splunk.

   **``linux:wtmpdb``**

   * name_rex: ``wtmp.*\.jsonl$``
   * sourcetype: ``linux:wtmpdb``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``
   * artifact: ``wtmpdb``

Description
-----------

Parsing login sessions from '/var/log/wtmp.db' (wtmpdb, Debian 13+/openSUSE/Fedora 42+)

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
