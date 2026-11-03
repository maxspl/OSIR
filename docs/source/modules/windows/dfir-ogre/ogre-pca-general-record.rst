ogre-pca-general-record
=======================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:pca_general_record`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of pca\_general\_record - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-pca_general_record-app-launch:

.. list-table::
   :header-rows: 1

   * - process.executable
     - Relation
     - Message
   * - 
     - `app-launch <rel-windows-dfir-ogre-pca_general_record-app-launch_>`_
     - ``Program {process.executable} was launched``

Relationships
-------------

.. _rel-windows-dfir-ogre-pca_general_record-app-launch:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `app-launch <tl-windows-dfir-ogre-pca_general_record-app-launch_>`_
     - ``host.name``
     - ``process.executable``
     - ``launched``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows Program Compatibility Assistant (PCA)"``
     - ``event.provider``
   * - ``executable_path``
     - ``process.executable``
   * - ``executable_path``
     - ``file.path``
   * - ``split!(to_string!(.executable_path), "\\")[-1]``
     - ``file.name``
   * - ``file_description``
     - ``file.description``
   * - ``file_version``
     - ``file.version``
   * - ``software_vendor``
     - ``process.pe.company``
   * - ``program_id``
     - ``action.properties.program_id``
   * - ``to_int(run_status)``
     - ``action.properties.run_status``
   * - ``exitcode_value``
     - ``action.properties.exitcode_value``
   * - ``parse_timestamp(run_time)``
     - ``timestamp``
   * - ``custom``
     - 
