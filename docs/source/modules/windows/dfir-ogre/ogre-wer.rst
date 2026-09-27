ogre-wer
========

.. tip:: Ingestion into Splunk.

   **``windows:ogre:wer``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``ogre-wer``
   * sourcetype: ``windows:ogre:wer``
   * host_rex: ``([\w\.-]+)--``
   * artifact: ``WER``
   * timestamp_path: ``modification_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S.%f%z``

Description
-----------

Parsing of wer - using ANSSI DFIR OGRE

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
