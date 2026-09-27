uac_log
=======

.. tip:: Ingestion into Splunk.

   **``uac:log``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``uac_log``
   * sourcetype: ``uac:log``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``ts``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``uac_log``

Description
-----------

Parse the UAC acquisition log (uac-\\*.log) and execution log (uac.log)

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
