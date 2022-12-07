def make_content(web_address):
    content = f"""
AUTHOR = 'NquiringMinds'
SITENAME = 'D3DB'
SITEURL = '{web_address}'

PATH = 'content'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

MENUITEMS = ()

# Can include multiple paths
PLUGIN_PATHS = ['plugins-extra']
PLUGINS = ['graphviz'] # adds support for graphviz graphs in markdown - https://github.com/pelican-plugins/graphviz

# Whether to display pages on the menu of the template. Templates may or may not honor this setting.
DISPLAY_PAGES_ON_MENU = False

# Whether to display categories on the menu of the template.
DISPLAY_CATEGORIES_ON_MENU = False

ARTICLE_URL = 'type/{{slug}}/'
ARTICLE_SAVE_AS = 'type/{{slug}}/index.html'
ARTICLE_ORDER_BY = 'title'

# Delete the output directory, and all of its contents, before generating new files.
# This can be useful in preventing older, unnecessary files from persisting in your output.
# However, this is a destructive setting and should be handled with extreme care.
DELETE_OUTPUT_DIRECTORY = True

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'https://getpelican.com/'),
         ('Python.org', 'https://www.python.org/'),
         ('Jinja2', 'https://palletsprojects.com/p/jinja/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

# Articles per page
DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

"""
    return content


def write_pelican_config(output_path, web_address):
    content = make_content(web_address)
    with open(output_path / 'pelicanconf.py', 'w') as f:
        print(content, file=f)
