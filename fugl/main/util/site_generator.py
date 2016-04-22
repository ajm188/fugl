import os
import tempfile
import shlex
import zipfile
from collections import Counter
from datetime import datetime
from subprocess import Popen

from django.utils.text import slugify


class GeneratedSite(object):

    def __init__(self, title, timestamp, archive):
        self.title = title
        self.timestamp = timestamp
        self.archive = archive

    def filename(self):
        strtime = self.timestamp.strftime('%Y-%m-%d_%H%M')
        filename = '{title}_output_{timestamp}.zip'.format(title=self.title,
                                                           timestamp=strtime)
        return filename

    def content_disposition_str(self):
        format_str = 'attachment; filename={filename}'
        return format_str.format(filename=self.filename())

    def content_length(self):
        return len(self.archive)


class SiteGenerator(object):

    def __init__(self, project):
        self.project = project

    def generate(self):
        archive = None
        with tempfile.TemporaryDirectory() as site_dir:
            self.generate_site_dir(site_dir)
            returncode = pelican_generate(
                site_dir,
                'content',
                'pelicanconf.py',
            )
            if returncode != 0:
                raise RuntimeError(
                    'Pelican returned status: {0}'.format(returncode),
                )

            archive = self.zip_output(site_dir)

        return GeneratedSite(self.project.title, datetime.now(), archive)

    def zip_output(self, site_dir):
        # now zip the output (in RAM)...
        tempzipfile = tempfile.NamedTemporaryFile(delete=True)
        output_dir = os.path.join(site_dir, 'output')

        with zipfile.ZipFile(tempzipfile, 'w', zipfile.ZIP_DEFLATED) as arc:
            for dirpath, _, filenames in os.walk(output_dir):
                for filename in filenames:
                    path = os.path.join(dirpath, filename)
                    arc_path = os.path.relpath(path, output_dir)
                    arc.write(path, arc_path)

        # load the zipfile's content into memory...
        with open(tempzipfile.name, 'rb') as f:
            content = f.read()
        tempzipfile.close()
        return content

    def generate_site_dir(self, site_dir):
        self.write_pelican_conf(site_dir)

        content_counter = Counter()
        written_pages = self.write_pages(
            self.project.page_set.all(),
            content_counter,
            site_dir,
        )
        written_posts = self.write_posts(
            self.project.post_set.all(),
            content_counter,
            site_dir,
        )
        slug_dict = {'pages': written_pages, 'posts': written_posts}
        self.write_page_plugins(self.get_plugin_dict(slug_dict), site_dir)

    def get_plugin_dict(self, slug_dict):
        plugin_dict = {'pages': {}, 'posts': {}}
        for page, slug in slug_dict['pages']:
            head = '\n'.join([p.head_markup for p in page.post_plugins.all()])
            body = '\n'.join([p.body_markup for p in page.post_plugins.all()])
            plugin_dict['pages'][slug] = (head, body)

        for post, slug in slug_dict['posts']:
            head = '\n'.join([p.head_markup for p in post.post_plugins.all()])
            body = '\n'.join([p.body_markup for p in post.post_plugins.all()])
            plugin_dict['posts'][slug] = (head, body)
        plugin_dict_str = str(plugin_dict)
        return plugin_dict_str

    def write_pages(self, pages, content_counter, site_dir):
        written_pages = []
        # Write each Page into `content/pages/`
        for page in pages:
            page_dir = os.path.join(site_dir, 'content', 'pages')
            mkdirs(page_dir)

            filename = get_filename(page, content_counter)
            written_pages.append((page, filename))
            page_file = os.path.join(page_dir, filename) + '.md'
            with open(page_file, 'w') as f:
                f.write(page.get_markdown(slug=filename))
        return written_pages

    def write_posts(self, posts, content_counter, site_dir):
        written_posts = []
        # Write each Post into `content/<category>`
        for post in posts:
            post_dir = os.path.join(
                site_dir,
                'content',
                slugify(post.category.title),
            )
            mkdirs(post_dir)

            filename = get_filename(post, content_counter)
            written_posts.append((post, filename))
            post_file = os.path.join(post_dir, filename) + '.md'
            with open(post_file, 'w') as f:
                f.write(post.get_markdown(slug=filename))
        return written_posts

    def write_pelican_conf(self, site_dir):
        with open(os.path.join(site_dir, 'pelicanconf.py'), 'w') as f:
            f.write(self.project.get_pelican_conf())

    def write_page_plugins(self, plugin_dict, site_dir):
        context = {'plugin_dict': plugin_dict}
        with open(os.path.join(site_dir, 'page_plugins.py'), 'w') as f:
            f.write(PLUGIN_BODY % context)


def get_filename(pagelike, pagelike_counter):
    """
    Return the filename for a Page/Post. Accomodates duplicates.
    """
    pagelike_filename = pagelike.filename
    while True:  # guaranteed to terminate for a finite number of pages
        pagelike_counter[pagelike_filename] += 1
        count = pagelike_counter[pagelike_filename]
        if count > 1:
            pagelike_filename += ('_%d' % (count,))
        else:
            break
    return pagelike_filename


def pelican_generate(site_dir, content_dir, settings_file, timeout=10):
    path_to_content = os.path.join(site_dir, content_dir)
    path_to_settings = os.path.join(site_dir, settings_file)
    cmd = ('pelican %(path_to_content)s -s %(path_to_settings)s' % {
        'path_to_content': path_to_content,
        'path_to_settings': path_to_settings,
    })
    p = Popen(shlex.split(cmd))
    p.wait(timeout=timeout)  # we don't have all day
    return p.returncode


def mkdirs(dir):
    try:
        os.makedirs(dir)
    except OSError:
        # if we fail, we don't care
        pass


PLUGIN_BODY = '''
from pelican import signals


def add_page_plugin(generator, **kwargs):
    d = kwargs['metadata']
    h, b = PLUGINS['pages'].get(d['slug'], (None, None))
    d['head_markup'] = h
    d['body_markup'] = b
    return kwargs


def add_post_plugin(generator, **kwargs):
    d = kwargs['metadata']
    h, b = PLUGINS['posts'].get(d['slug'], (None, None))
    d['head_markup'] = h
    d['body_markup'] = b
    return kwargs


PLUGINS = %(plugin_dict)s


def register():
    signals.article_generator_context.connect(add_post_plugin)
    signals.page_generator_context.connect(add_page_plugin)
'''
