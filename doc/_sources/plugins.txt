Plugins
=======

As you've probably read by now, plugins are bits of code that get mixed into
your site to alter its behavior. If you don't know much about code or HTML,
that's fine -- you don't need to! This article will describe a few different
types of plugins which you can easily add to your project.


Project Plugins
---------------

Project plugins are plugins that are applied to every single page in your site.
They don't usually show up visibly on your site content, but rather they can
make your site do interesting things. Here's an example of some code that you
could put into a project plugin:

.. code:: html

   <script>
     alert("I'm an annoying popup!");
   </script>

If you're not familiar with HTML or Javascript, this code will make a little
message box pop up proclaiming "I'm an annoying popup!". Since project plugins
are added to every single page in your site, this plugin would interrupt your
site's user every time they go to a new page with a new popup. Clearly, this
isn't a useful plugin, but hopefully it gets the idea across.

So what sort of useful plugins can you add to your site? Well, perhaps the most
useful site-wide plugin you could add to a site is something called Google
Analytics. This product from Google will collect useful information about your
site's visitors and their behavior. This is very useful for understanding the
type of people that use your site, so that you can better cater to your
visitors. In order to get Google Analytics up and running, you'll have to do
two things:

1. Set up a Google Analytics account and create a "property" for your website.
   See Google's `help
   <https://support.google.com/analytics/answer/1008015?hl=en>`_ document about
   this process for more information.
2. From your Fugl project's home, click the "Project Plugins" dropdown, and
   select "New Project Plugin".
3. In the "Title" field [#projplugtitle]_, enter "Google Analytics".
4. Get your web tracking code for your site on Google Analytics. Instructions
   for doing this are on `this help document
   <https://support.google.com/analytics/answer/1008080>`_ by Google. You want
   to follow the instructions under "Add the tracking code directly to your
   site."  Copy and paste your tracking code into the "Markup" field.
5. Click Submit.

Once you download a new zip and deploy to your web host, you should be able to
watch live analytics information for your website on Google Analytics!

.. [#projplugtitle] A project plugin may have any title you'd like! It's just
                    for you to remember what it is -- it won't show up on your
                    site.

Page Plugins
------------

Page Plugins are a bit different from Project Plugins. Unlike project plugins,
these only go on specific Pages. Once you've created a Page Plugin, you can
edit your pages and add the plugin to whatever pages you'd like. The other
major difference is that Page Plugins typically add content to your page,
rather than just make your site do cool things. Typically they have two parts:
head markup and body markup, with head markup guaranteed to go before body
markup. First, here are some instructions on how to add Page Plugins to your
site:

1. From the Project Homepage, click the "Page Plugins" dropdown. Click "New
   Page Plugin".
2. Enter a title (this will depend on what your plugin is for). Your title can
   be anything; it's just for your organization. The title won't show up on
   your site.
3. Paste the head and body markup in (you will see some examples shortly).
4. Click Submit.

To add a Page Plugin to a Page:

1. Click the Page title in the Project Home. This will take you to the Edit
   Page screen.
2. You should now see the title of your Page Plugin under the "Plugins" heading.
   You can select it for this page. If you'd like to select multiple plugins,
   hold the control button while you click.
3. Click Submit.

Now, when you download your site again, you will have the plugin on this page.
You may have to repeat this process for each page you'd like this plugin to
appear on. There is currently no way to automatically add a plugin to many
pages, although this feature could be added in the future.

Disqus Comments
---------------

So now that you know all about creating page plugins and adding them to pages,
what can you do with a page plugin? Well, one of the best things to do is add
Disqus! Disqus is a system that puts a comment section on a page, without any
extra complexity to you. To use Disqus, you'll need to create an account
(`start here <https://disqus.com/>`_ for that). Once you have an account, you
can `create <https://disqus.com/admin/create/>`_ your own site profile.

Next, get your "universal code" by going to this URL:

.. code::

   https://[shortname].disqus.com/admin/settings/universalcode/

Here, ``shortname`` is the Disqus shortname you should have created in the
previous step. Copy and paste the universal code into the "body markup" section
of a page plugin.

Now, when you add this plugin to a page, download the ZIP, and deploy, you'll
have comments built in to your website on that page!

Social Media Buttons
--------------------

When you're trying to gain popularity on a website, one of the best things you
can do is make it easy for your visitors to share content from your site. For
instance, if you've written a particularly good blog article, you should make
it easy for readers to share it to Facebook, Twitter, and other social media
platforms. Social media buttons make this easy.

There are many ways you can add social buttons, but the most straightforward
way is to use a free tool to generate code you can put into a Fugl plugin.
One free example is called `Share This <http://www.sharethis.com/>`_.

1. Create a Share This account (all that is required is an email and password).
2. Go to the `homepage <http://www.sharethis.com/>`_ and click "Free Sharing
   Buttons".
3. Click "Website".
4. Select the style of the buttons that you'd prefer on your site.
5. Customize which social media platforms you'd like to target.
6. When you are done, click "Get the code".
7. The first block of code they give you (under number 2) should be pasted into
   the body markup of a Page Plugin.
8. The second block of code (under number 3) should be pasted into the head
   markup section of the same Page Plugin.
9. Every page and post you add this plugin to will have social media sharing
   buttons enabled!
