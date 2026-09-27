authlog
=======

.. tip:: Ingestion into Splunk.

   **``linux:authlog``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``authlog``
   * sourcetype: ``linux:authlog``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``ts``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``
   * artifact: ``auth``

Description
-----------

Parse auth log from UAC [root] using Dissect plugin

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
