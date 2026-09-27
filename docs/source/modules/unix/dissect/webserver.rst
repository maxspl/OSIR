webserver
=========

.. tip:: Ingestion into Splunk.

   **``linux:webserver``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``webserver``
   * sourcetype: ``linux:webserver``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``ts``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``
   * artifact: ``webserver``

Description
-----------

Parse webserver access,certificates,error,hosts,logs from UAC [root] using Dissect plugin

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
