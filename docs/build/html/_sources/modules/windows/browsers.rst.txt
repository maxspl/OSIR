browsers
========

.. tip:: Ingestion into Splunk.

   **``application:chrome``**

   * name_rex: ``.*chrome.*\.jsonl$``
   * path_suffix: ``browsers``
   * sourcetype: ``application:browser:chrome``
   * host_rex: ``([\w\.-]+)--``

   **``application:edge``**

   * name_rex: ``.*edge.*\.jsonl$``
   * path_suffix: ``browsers``
   * sourcetype: ``application:browser:edge``
   * host_rex: ``([\w\.-]+)--``

   **``application:firefox``**

   * name_rex: ``.*firefox.*\.jsonl$``
   * path_suffix: ``browsers``
   * sourcetype: ``application:browser:firefox``
   * host_rex: ``([\w\.-]+)--``

Description
-----------

Parsing of browsers artifact.

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
