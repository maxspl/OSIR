ssh
===

.. tip:: Ingestion into Splunk.

   **``linux:ssh``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ssh``
   * sourcetype: ``linux:ssh``
   * host_rex: ``([\w\.-]+?)--``
   * artifact: ``ssh``

Description
-----------

Parse ssh authorized\_keys,known\_hosts,private\_keys,public\_keys,config,session from UAC [root] using Dissect plugin

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
