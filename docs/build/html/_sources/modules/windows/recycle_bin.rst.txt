recycle_bin
===========

.. tip:: Ingestion into Splunk.

   **``windows:recyclebin``**

   * name_rex: ``\.csv$``
   * path_suffix: ``recycle_bin``
   * sourcetype: ``windows:files:recyclebin``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``DeletedOn``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S``

Description
-----------

Parsing of recycle bin artifact.

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
