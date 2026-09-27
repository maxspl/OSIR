journal
=======

.. tip:: Ingestion into Splunk.

   **``linux:journal``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``journal``
   * sourcetype: ``linux:journal``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``__REALTIME_TIMESTAMP``
   * artifact: ``journal``

Description
-----------

Parsing logs from '/var/log/journal/'

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
