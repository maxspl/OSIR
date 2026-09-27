srum
====

.. tip:: Ingestion into Splunk.

   **``windows:srum``**

   * name_rex: ``--srum-.*\.jsonl$``
   * sourcetype: ``windows:files:srum``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``SRUM``
   * normalize: ``ecs_normalize/windows/srum.vrl``
   * encoding: ``utf8``

Description
-----------

Parsing of SRUM artifact.

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
