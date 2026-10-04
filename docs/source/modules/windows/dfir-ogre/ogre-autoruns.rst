ogre-autoruns
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:autoruns`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of autoruns - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-autoruns-autoruns-entry:
.. _tl-windows-autoruns-autoruns-key:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `autoruns-entry <rel-windows-autoruns-autoruns-entry_>`_
     - ``Autoruns entry {process.executable} registered at {registry.path}``
   * - ``autoruns-key``
     - ``Autoruns registry key {registry.path} of type {labels.autoruns_type} exists``

Relationships
-------------

.. _rel-windows-autoruns-autoruns-entry:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `autoruns-entry <tl-windows-autoruns-autoruns-entry_>`_
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
   * - ``"windows.autoruns"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process, registry]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"Windows Autoruns (dfir-ogre)"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
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
     - ``labels.pe_sha1``
   * - ``pe_sha256``
     - ``labels.pe_sha256``
   * - ``entry_name``
     - ``labels.entry_name``
   * - ``entry``
     - ``labels.entry``
   * - ``category``
     - ``labels.category``
   * - ``profile``
     - ``labels.profile``
   * - ``description``
     - ``labels.description``
   * - ``company``
     - ``labels.company``
   * - ``signer``
     - ``labels.signer``
   * - ``version``
     - ``labels.version``
   * - ``imp``
     - ``labels.imp``
   * - ``parse_timestamp(time)``
     - ``timestamp``
   * - ``ogre_md``
     - ``labels.ogre_md``
   * - ``key_path``
     - ``registry.path``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``parse_timestamp(key_modif_time)``
     - ``timestamp``
   * - ``type``
     - ``labels.autoruns_type``
   * - ``values``
     - ``labels.values``
   * - ``key_security``
     - ``labels.key_security``
   * - ``ogre_md``
     - ``labels.ogre_md``
