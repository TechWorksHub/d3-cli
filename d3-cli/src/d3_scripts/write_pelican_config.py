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
FILENAME_METADATA = '(?P<title>.*)'  # use filename as metadata title by default
DEFAULT_DATE = "fs"  # use file system modified date as date by default

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
LINKS = (
         ('Github D3DB', 'https://github.com/TechWorksHub/ManySecured-D3DB'),
         ('Pelican', 'https://getpelican.com/'))

# Social widget
SOCIAL = (('NquiringMinds', 'https://nquiringminds.com/'),)

# Articles per page
DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

STATIC_PATHS = []

"""
    return content


def write_pelican_config(output_path, web_address):
    content = make_content(web_address)
    with open(output_path / 'pelicanconf.py', 'w') as f:
        print(content, file=f)
