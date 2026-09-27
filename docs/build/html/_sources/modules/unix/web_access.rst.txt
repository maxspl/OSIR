web_access
==========

.. tip:: Ingestion into Splunk.

   **``linux:web_access``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``web_access``
   * sourcetype: ``linux:web_access``
   * host_rex: ``-([\w\.-]+?)--``
   * timestamp_path: ``ts``, ``ts_raw``
   * timestamp_format: ``%d/%b/%Y:%H:%M:%S.%f %z``
   * artifact: ``web_access``

Description
-----------

Parsing web access logs

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
