ogre-evtx
=========

.. tip:: Ingestion into Splunk.

   **``windows:ogre:evtx``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-evtx``
   * sourcetype: ``windows:ogre:evtx``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``EVTX``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of EVTX collected by DFIR ORC or in the filesystem - using ANSSI DFIR OGRE

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
