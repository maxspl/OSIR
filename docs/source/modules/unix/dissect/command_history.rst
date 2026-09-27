command_history
===============

.. tip:: Ingestion into Splunk.

   **``linux:command_history``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``command_history``
   * sourcetype: ``linux:command_history``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``ts``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``
   * artifact: ``bash_history``

Description
-----------

Parse .$SHELL\_history from UAC [root] using Dissect plugin

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
