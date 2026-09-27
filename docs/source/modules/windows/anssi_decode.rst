anssi_decode
============

.. tip:: Ingestion into Splunk.

   **``windows:decode``**

   * name_rex: ``decode_result_\w+\.csv``
   * sourcetype: ``anssi:decode``
   * host_rex: ``anssi_decode\/(.*?)\/``
   * timestamp_path: ``FileNameLastModificationDate``
   * timestamp_format: ``%Y-%m-%d %H:%M:%S.%f``
   * artifact: ``decode``

Description
-----------

ANSSI tool designed for detecting anomalous Portable Executable (PE) files among the NTFSInfo data collected by DFIR-ORC

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
