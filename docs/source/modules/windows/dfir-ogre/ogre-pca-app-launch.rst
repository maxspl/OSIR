ogre-pca-app-launch
===================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:pca_app_launch`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of pca\_app\_launch - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-pca_app_launch-app-launch:

.. list-table::
   :header-rows: 1

   * - process.executable
     - Relation
     - Message
   * - 
     - `app-launch <rel-windows-dfir-ogre-pca_app_launch-app-launch_>`_
     - ``Program {process.executable} was launched``

Relationships
-------------

.. _rel-windows-dfir-ogre-pca_app_launch-app-launch:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `app-launch <tl-windows-dfir-ogre-pca_app_launch-app-launch_>`_
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
   * - ``parse_timestamp(timestamp)``
     - ``timestamp``
   * - ``custom``
     - 
