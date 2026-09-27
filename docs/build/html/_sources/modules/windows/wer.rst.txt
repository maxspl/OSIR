wer
===

.. tip:: Ingestion into Splunk.

   **``windows:wer``**

   * name_rex: ``--wer\.jsonl$``
   * path_suffix: ``wer``
   * host_rex: ``([\w\.-]+)--``
   * timestamp_path: ``timestamp``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%SZ``
   * artifact: ``WER``
   * normalize: ``ecs_normalize/windows/wer.vrl``

Description
-----------

Parse .wer files

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
