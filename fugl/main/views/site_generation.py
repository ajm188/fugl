from django.views.generic.base import View
from django.utils.text import slugify
from django.template.response import TemplateResponse
from django.http import HttpResponse
from main.models import Project
from .protected_view import ProtectedViewMixin
from subprocess import Popen
from datetime import datetime
from collections import Counter
from pprint import pprint
import tempfile
import zipfile
import shlex
import os


class SiteGenerationView(ProtectedViewMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            return self._do_generate(request, args, kwargs)
        except Exception as e:
            pprint(e)
            ctx = {
                'message': "Actually, we derped. You can redeem this"
                           " page for a free hug from the Fugle. Sorry :(",
                'link_url': '/project/{0}/{1}'.format(kwargs['owner'], kwargs['proj_title']),
                'link_text': 'Return to Project Home',
            }
            return TemplateResponse(request, 'error.html', context=ctx)

    def _do_generate(self, request, *args, **kwargs):
        project_title = request.resolver_match.kwargs['proj_title']
        project = Project.objects.get(owner=request.user, title=project_title)

        with tempfile.TemporaryDirectory() as site_dir:
            # Put settings and plugin(s) in the root
            with open(os.path.join(site_dir, 'pelicanconf.py'), 'w') as f:
                f.write(project.get_pelican_conf())

            p2slug = {'pages': [], 'posts': []}
            # Write each Page into `content/pages/`
            pagelike_counter = Counter()
            for page in project.page_set.all():
                page_dir = os.path.join(site_dir, 'content', 'pages')
                mkdirs(page_dir)

                filename = get_filename(page, pagelike_counter)
                p2slug['pages'].append((page, filename))
                page_file = os.path.join(page_dir, filename) + '.md'
                with open(page_file, 'w') as f:
                    f.write(page.get_markdown(slug=filename))

            # Write each Post into `content/<category>`
            for post in project.post_set.all():
                post_dir = os.path.join(site_dir, 'content', slugify(post.category.title))
                mkdirs(post_dir)

                filename = get_filename(post, pagelike_counter)
                p2slug['posts'].append((post, filename))
                post_file = os.path.join(post_dir, filename) + '.md'
                with open(post_file, 'w') as f:
                    f.write(post.get_markdown(slug=filename))

            context = {
                'plugin_dict': get_plugin_dict(p2slug)
            }
            with open(os.path.join(site_dir, 'page_plugins.py'), 'w') as f:
                f.write(PLUGIN_BODY % context)

            # now that we've written out all files, call into pelican
            returncode = pelican_generate(site_dir, 'content', 'pelicanconf.py')
            if returncode != 0:
                raise RuntimeError('Pelican returned status: {0}'.format(returncode))

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

            # ...and return the zipfile to the user
            filename = '{0}_output_{1}.zip'.format(project.title,
                                                   datetime.now().strftime('%Y-%m-%d_%H%M'))
            resp = HttpResponse(content, content_type='application/zip')
            resp['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
            resp['Content-Length'] = len(content)
            return resp


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


def get_plugin_dict(p2slug):
    plugin_dict = {'pages': {}, 'posts': {}}
    for page, slug in p2slug['pages']:
        head = '\n'.join([p.head_markup for p in page.post_plugins.all()])
        body = '\n'.join([p.body_markup for p in page.post_plugins.all()])
        plugin_dict['pages'][slug] = (head, body)

    for post, slug in p2slug['posts']:
        head = '\n'.join([p.head_markup for p in post.post_plugins.all()])
        body = '\n'.join([p.body_markup for p in post.post_plugins.all()])
        plugin_dict['posts'][slug] = (head, body)
    plugin_dict_str = str(plugin_dict)
    return plugin_dict_str


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
