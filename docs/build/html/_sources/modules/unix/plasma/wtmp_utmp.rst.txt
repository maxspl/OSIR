wtmp_utmp
=========

.. tip:: Ingestion into Splunk.

   **``linux:wtmp_utmp``**

   * name_rex: ``\.jsonl$``
   * path_suffix: ``wtmp_utmp``
   * sourcetype: ``linux:wtmp_utmp``
   * host_rex: ``([\w\.-]+?)--``
   * timestamp_path: ``ut_time``
   * timestamp_format: ``%Y-%m-%dT%H:%M:%S%z``
   * artifact: ``wtmp_utmp``

Description
-----------

Login records from binary utmp/wtmp/btmp using the CERT-EDF plasma dissector

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
