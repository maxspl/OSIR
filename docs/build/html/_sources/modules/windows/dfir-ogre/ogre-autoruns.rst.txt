ogre-autoruns
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:sysinternals:autoruns`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of autoruns - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-autoruns-autoruns-entry:

.. list-table::
   :header-rows: 1

   * - registry.path
     - Relation
     - Message
   * - 
     - `autoruns-entry <rel-windows-dfir-ogre-autoruns-autoruns-entry_>`_
     - ``Autoruns entry {process.executable} registered at {registry.path}``

Relationships
-------------

.. _rel-windows-dfir-ogre-autoruns-autoruns-entry:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `autoruns-entry <tl-windows-dfir-ogre-autoruns-autoruns-entry_>`_
     - ``registry.path``
     - ``process.executable``
     - ``launches``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"Windows Autoruns (dfir-ogre)"``
     - ``event.provider``
   * - ``entry_location``
     - ``registry.path``
   * - ``image_path``
     - ``process.executable``
   * - ``launch_string``
     - ``process.command_line``
   * - ``image_path``
     - ``file.path``
   * - ``md5``
     - ``file.hash.md5``
   * - ``sha1``
     - ``file.hash.sha1``
   * - ``sha256``
     - ``file.hash.sha256``
   * - ``pe_sha1``
     - ``action.properties.pe_sha1``
   * - ``pe_sha256``
     - ``action.properties.pe_sha256``
   * - ``entry_name``
     - ``action.properties.entry_name``
   * - ``entry``
     - ``action.properties.entry``
   * - ``category``
     - ``action.properties.category``
   * - ``profile``
     - ``action.properties.profile``
   * - ``description``
     - ``action.properties.description``
   * - ``company``
     - ``action.properties.company``
   * - ``signer``
     - ``action.properties.signer``
   * - ``version``
     - ``action.properties.version``
   * - ``imp``
     - ``action.properties.imp``
   * - ``parse_timestamp(time)``
     - ``timestamp``
