apt_history
===========

.. tip:: Ingestion into Splunk.

   **``linux:apt_history``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``apt_history``
   * sourcetype: ``linux:apt_history``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``hist_beg_time``
   * timestamp_format: ``%Y-%m-%d  %H:%M:%S``
   * artifact: ``apt_history``

Description
-----------

Package install/remove history from /var/log/apt/history.log

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
