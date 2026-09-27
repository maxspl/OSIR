# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# Paths are resolved relative to this conf.py file so the documentation always
# describes the code of the current repository, whatever the directory
# sphinx-build is started from.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OSIR_DIR = os.path.join(REPO_ROOT, 'OSIR')

# Add the OSIR directory so the 'src' package (used by the generated API doc
# pages, e.g. src.osir_api.osir_api) is importable
sys.path.insert(0, OSIR_DIR)

# Add each package directory so internal imports (osir_service, osir_lib, ...)
# resolve to the packages of the current repository
for _pkg in ('osir_api', 'osir_client', 'osir_lib', 'osir_service', 'osir_vrl'):
    sys.path.insert(0, os.path.join(OSIR_DIR, 'src', _pkg))
project = 'OSIR'
copyright = '2024, maxspl - Typ'
author = 'maxspl - Typ'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Optional, for Google-style docstrings
    'sphinx.ext.viewcode',  # Optional, for viewing source code
    'sphinxcontrib.video',
    'myst_parser'  # to include the packages README.md files
]

# Render Google-style "Attributes:" docstring sections as :ivar: fields
# instead of .. attribute:: directives, so they don't duplicate the object
# descriptions already produced by autodoc for the real class attributes.
napoleon_use_ivar = True

# Some module YAML files contain regexes with "\/" escapes in double-quoted
# strings, which the pygments YAML lexer rejects (they are still highlighted
# in relaxed mode). The proper fix belongs to the module configuration files.
suppress_warnings = ['misc.highlighting_failure']

templates_path = ['_templates']
# extracted_module_info.md is a side artifact of modules_summary.py, the
# documentation only uses the .rst version.
exclude_patterns = ['extracted_module_info.md']

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'private-members': False,
    'special-members': '__init__',
    'inherited-members': False,
    'show-inheritance': True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinxawesome_theme'
html_title = 'Orchestration Software for Incident Response'
html_static_path = ['_static']
html_css_files = ['module-cards.css', 'tables.css']
html_js_files = ['sidebar-scroll.js']

# Remove the permanent anchor links after each heading
html_permalinks = False

# Sidebar: custom "Overview" block (a single page with links to its
# sections) rendered above the global toctree navigation.
html_sidebars = {
    '**': [
        'overview_menu.html',
        'sidebar_toc.html',
    ],
}
