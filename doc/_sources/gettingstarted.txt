Getting Started
===============

Create your account
-------------------

In order to use Fugl, you need to have a user account.  All of your projects
will be associated with your user account, so make sure you use a good password!

1. Go to https://fugl.xyz/register
2. Enter a username [#un]_, email address, and password, and then click submit.
3. You should be redirected to the login page.
4. Enter your username and password, and you'll be presented with your account
   homepage.

.. [#un] A valid username must be 30 characters or fewer, and consist of
         letters, digits, and the following characters: ``@.+-_``

Create your first project
-------------------------

The account homepage gives you the ability to manage all of your projects.  In
Fugl, a project represents a website.  From the account home, you can create,
duplicate, and delete projects.  We'll start by creating a simple example
project to help you understand what Fugl lets you do.

1. Click the "New Project" button.
2. In the "Title" field [#title]_, enter a title.  For the purpose of this
   example, you can enter something like "My First Website".
3. In the "Description" [#desc]_ field, enter a sentence that describes the
   purpose of your website.  For this example, you can use something like "I'm
   learning to use Fugl!".
4. You should be redirected to your project homepage.

.. [#title] A valid title may contain: letters, digits, hyphens, and spaces.
.. [#desc] A description may contain anything!

Create your first page
----------------------

From the project homepage, you have access to all of your major project
management commands.  The most important things you'll do at your project
homepage are create and update pages and posts.  A "page" is a page on your
website that isn't a blog post.  For instance, "about us" and "contact us" are
common pages on a site.  Posts, on the other hand, are blog posts.  They are
published and displayed on your blog in order of publication date.

So, if you're making a simple site, the first thing you'll probably want to do
is make an "About Us" page:

1. Click the "New Page" button.
2. In the "Title" field [#artitle]_, enter "About Us".
3. In the "Content" field, type or paste the following:

   .. code::

      # What is Fugl?
   
      Fugl is an application for making simple static websites.  Your pages
      are written in Markdown, so you can create [links](https://fugl.xyz),

      - bulleted
      - lists,

      *italicize*, **make text bold**, and

      ---

      create horizontal rules.

   You should notice that as you type, the area below the text field dynamically
   updates with a live preview of how your page will be displayed on your site.
   Your pages and posts are written using `Markdown
   <https://daringfireball.net/projects/markdown/>`_, which is a simple system
   for creating formatted text.  See the provided link for information about how
   to use Markdown, as wall as the above text for examples of some of the basics
   features of Markdown.  You can use the editor's built-in buttons for
   inserting formatting elements if you'd rather not spend any time learning
   Markdown.

4. Once you hit "Submit", the page will be saved and you will be redirected back
   to your project home.
5. If you'd like to make changes to the page, you can click on the page's name
   in the "Page" list to edit it.

.. [#artitle] Article and post titles can be anything, although when they are
              translated into files on your site, they will be altered slightly
              (to remove spaces and unusual spaces, as well as resolve duplicate
              titles).

Create your first post
----------------------

You can follow a similar procedure for creating posts (click the "New Post"
button instead).  You may want to use a different title for the first post.  If
you'd like to associate your post with a particular category, you'll have to
first click the "Categories" drop-down, and then select "New Category" to create
one.  However, Posts do not have to be associated with categories.

Changing your site's theme
--------------------------

Your site is created with a nice default theme.  However, you may want to "spice
up" your site with a different theme.  To do this:

1. From your project home, click "Project Settings".
2. Select "html5-dopetrope" from the Theme drop-down box.
3. Click Submit.  You are returned to your project homepage.

Now, your project's theme will be different.  If you'd like to see previews for
some of the themes available within Fugl, please check `this
<http://www.pelicanthemes.com/>`_ website.  Right now, Fugl only supports a
few of the themes shown on this site, but this can be easily expanded!

Download your site!
-------------------

Now that you have some content created for your website, you can click "Download
ZIP".  A ZIP file containing your generated website will begin downloading.  You
can give this ZIP file to your web host to deploy, or you can extract it and
upload it via FTP to your web server directly.  Enjoy your new site!

If you'd like to preview your site before deploying, you'll need to unzip the
file and preview it using a web server.  This is important because otherwise
your themes won't display properly when you preview.
