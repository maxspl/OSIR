ogre-registry-shell-bag
=======================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:registry:shell_bag`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of shellbags - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-registry-shell_bags-interacted-with:
.. _tl-windows-dfir-ogre-registry-shell_bags-referenced:

.. list-table::
   :header-rows: 1

   * - action.properties.HasExplored
     - Relation
     - Message
   * - ``True``
     - `interacted-with <rel-windows-dfir-ogre-registry-shell_bags-interacted-with_>`_
     - ``User {user.name} interacted with {action.properties.AbsolutePath}``
   * - ``False``
     - `referenced <rel-windows-dfir-ogre-registry-shell_bags-referenced_>`_
     - ``Shellbag entry exists for {action.properties.AbsolutePath} (no evidence of user interaction)``

Relationships
-------------

.. _rel-windows-dfir-ogre-registry-shell_bags-interacted-with:
.. _rel-windows-dfir-ogre-registry-shell_bags-referenced:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `interacted-with <tl-windows-dfir-ogre-registry-shell_bags-interacted-with_>`_
     - ``user.name``
     - ``action.properties.value``
     - ``interacted with``
   * - `referenced <tl-windows-dfir-ogre-registry-shell_bags-referenced_>`_
     - ``user.name``
     - ``action.properties.value``
     - ``referenced``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``name``
     - ``action.properties.value``
   * - ``type``
     - ``action.properties.shell_type``
   * - ``localized_name``
     - ``action.properties.localized_name``
   * - ``description``
     - ``action.properties.description``
   * - ``file_reference``
     - ``file.inode``
   * - ``replace(to_string!(.path), pattern: "\\\\", with: "\\")``
     - ``action.properties.AbsolutePath``
   * - ``parse_timestamp(key_modif_time)``
     - ``timestamp``
   * - ``parse_timestamp(key_modif_time)``
     - ``registry.mtime``
   * - ``parse_timestamp(modification_time)``
     - ``file.mtime``
   * - ``parse_timestamp(access_time)``
     - ``file.accessed``
   * - ``parse_timestamp(creation_time)``
     - ``file.created``
   * - ``replace(to_string!(.key_path), pattern: "\\\\", with: "\\")``
     - ``registry.path``
   * - ``true``
     - ``action.properties.HasExplored``
