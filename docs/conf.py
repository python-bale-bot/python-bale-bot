# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import re

sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))

project = 'python-bale-bot'
copyright = '2022, Kian Ahmadian'
author = 'Kian Ahmadian'
with open('../bale/version.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

# The full version, including alpha/beta/rc tags.
release = version

# This assumes a tag is available for final releases
branch = 'master' if version.endswith('a') else 'v' + version



# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'builder',
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinxcontrib_trio',
    'details',
    'exception_hierarchy',
    'attributetable',
    'resourcelinks',
    'nitpick_file_ignorer',
]
master_doc = 'index'
source_suffix = '.rst'
autodoc_member_order = 'bysource'
autodoc_typehints = 'none'
gettext_compact = False
templates_path = ['_templates',]
include_patterns = ["**"]
exclude_patterns = ['build', ]
intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
  'req': ('https://requests.readthedocs.io/en/latest/', None)
}

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'basic'
html_static_path = ['_static']
html_show_sphinx = True
html_logo = "_static/images/bale.png"
html_favicon = "_static/images/bale.png"
html_css_files = ["css/style.css", "css/codeblocks.css"]
html_js_files = ["js/copy.js", "js/sidebar.js", "js/setting.js", "js/custom.js"]
html_context = {
  'discord_invite': 'https://discord.gg/bYHEzyDe2j',
  'bale_extensions': [],
}
resource_links = {
  'discord': 'https://discord.gg/bYHEzyDe2j',
  'issues': 'https://github.com/kian-ahmadian/python-bale-bot/issues',
  'discussions': 'https://github.com/kian-ahmadian/python-bale-bot/discussions',
  'examples': f'https://github.com/kian-ahmadian/python-bale-bot/tree/{branch}/examples',
}