ogre-registry-bamdam
====================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:registry:bamdam`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of bam\_dam - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-registry-bam_dam-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `executed <rel-windows-dfir-ogre-registry-bam_dam-executed_>`_
     - ``User {user.id} executed {process.executable} (last run {timestamp})``

Relationships
-------------

.. _rel-windows-dfir-ogre-registry-bam_dam-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `executed <tl-windows-dfir-ogre-registry-bam_dam-executed_>`_
     - ``user.id``
     - ``process.executable``
     - ``executed``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows BAM/DAM (Background Activity Monitor)"``
     - ``event.provider``
   * - ``exec_path``
     - ``process.executable``
   * - ``user_sid``
     - ``user.id``
   * - ``replace(to_string!(.key_path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``"HKLM"``
     - ``registry.hive``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``parse_timestamp(exec_time)``
     - ``timestamp``
