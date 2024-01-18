# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'python-bale-bot'
project_copyright = '2020-Present, Kian Ahmadian'
author = 'Kian Ahmadian'
release = version = '2.5.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
	"sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx_inline_tabs",
    "sphinx.ext.intersphinx"
]

master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = []
autodoc_typehints = "none"

autodoc_default_options = {
    "special-members": True,
    "exclude-members": ",".join(["__init__", "__str__", "__eq__", "__ne__", "__hash__", "__repr__", "__ge__", "__gt__", "__le__", "__lt__", "__weakref__"])
}
intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
  'aio': ('https://docs.aiohttp.org/en/stable/', None),
  'req': ('https://requests.readthedocs.io/en/latest/', None)
}
todo_include_todos = False
paramlinks_hyperlink_param = "name"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_favicon = "_static/images/bale.png"
html_logo = "_static/images/bale.png"
html_permalinks_icon = "¶"
html_baseurl = "https://docs.python-bale-bot.ir"
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
    "css/style.css",
    "css/sidebar.css",
    "css/announcement.css"
]
html_theme_options = {
    "sidebar_hide_name": True,
    "announcement": "برای دریافت اطلاعات بیشتر به <a href='https://python-bale-bot.ir'>سایت کتابخانه</a> مراجعه نمایید",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/python-bale-bot/python-bale-bot",
            "html": "",
            "class": "fa-brands fa-solid fa-github fa-2x",
        },
        {
            "name": "GitHub",
            "url": "https://python-bale-bot.ir",
            "html": "",
            "class": "fas fa-globe fa-2x",
        },
    ]
}
html_title = 'python-bale-bot v{}'.format(version)

man_pages = [(master_doc, "python-bale-bot", "python-bale-bot Documentation", [author], 1)]