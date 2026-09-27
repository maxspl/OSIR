Profiles
========

Profiles are YAML configuration files that define a set of modules to be executed. Each profile specifies the operating system, modules, and other metadata required for the process.

.. tip:: Profiles are located in OSIR/OSIR/configs/profiles. They can be placed in any subdirectory of this path, the directory name does not matter.

Example Profile
^^^^^^^^^^^^^^^

Below is an example profile `DFIR_ORC.yml`:

.. code-block:: yaml

    version: 1.0
    author:
    description:
    os: windows
    modules:
      - extract_orc.yml
      - evtx_orc.yml
      - test_process_dir
      - test_process_dir_multiple_output
      - prefetch
      - restore_fs
      - amcache.yml
      - chromium.yml
      - firefox.yml
      - hives_hklm.yml
      - hives_hkcu.yml
      - jump_list.yml
      - lnk.yml
      - recycle_bin.yml
      - shell_bags.yml
      - shimcache.yml
      - srum.yml
      - win_timeline.yml

Create a new profile
^^^^^^^^^^^^^^^^^^^^

To create a new profile, follow this structure :

.. code-block:: yaml

    version: 1.0
    author: author_name
    description: profile_description
    os: os_typ
    modules:
        - module1.yml
        - module2.yml
        - INPUT ALL THE MODULE YOU WANT

