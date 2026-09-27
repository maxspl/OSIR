orc_log
=======

.. tip:: Ingestion into Splunk.

   **``orc:log``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``orc_log``
   * sourcetype: ``orc:log``
   * host_rex: ``orc_log_(.+)_\d{8}_\d{6}\.jsonl$``
   * timestamp_path: ``ts``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``orc_log``

Description
-----------

Parse the DFIR ORC execution log (DFIR-ORC\_\\*.log) for run parameters, archives, commands and their outcome

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
