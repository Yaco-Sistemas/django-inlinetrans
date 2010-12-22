Introduction
============

Inlinetrans is a django application that allows the translation of django templates from the rendered html in the browser. Once you have your templates internationalized with inlinetrans, you can click on the untranslated messages in their corresponding web pages to add their translations. This can be of great help for translators, as they will be able to translate the messages right in their intended context.

Features
========

- A templatetag, **inline_trans**, intended as a replacement for django's **trans**.
- A management command, **inline_makemessage**, intended as a replacement for django's **makemessages**.
- A translation bar to show translatable messages, by default visible only to *staff* members.

To translate the messages in a web page rendered in your browser, you first find out, through the translation bar, which messages have already been translated (marked light green) and which ones lack translation (marked light red).

Then, you click on a marked message, and are prompted for its translation; on entering the text and clicking OK, the new translation is sent to the server and saved in the correct .po file.

Once you have translated all messages in a page, you can click on "apply changes" on the translation bar. This forces a restart on the server, and the reloading of the page with the translations applied.

Requirements
============

To use inlinetrans, you need:

- Jquery-1.2.6

Using inlinetrans
=================

Make sure media from inlinetrans is accessible in path:

   >>> {{ MEDIA_URL }}inlinetrans


You need to do a checkout of inlinetrans media on media path of your project or setting property externals on your media path.

   >>> svn checkout http://django-inlinetrans.googlecode.com/svn/trunk/inlinetrans/media inlinetrans


Make sure you load inlinetrans in all templates you want to internationalize, by adding the following code:

    >>>
    {% load inlinetrans %}
    {% inlinetrans_media %}


Then, you can use:

    >>> {% inline_trans "translate this" %}


Instead of:

    >>> {% trans "translate this" %}


Inlinetrans adds html code to each translation, so make sure you don't use **inline_trans** tags inside html attributes, such as this:

    >>> <a href="#" alt="{% inline_trans "translate this" %}"></a>


In these cases you have to use the regular **trans** tag.

Once your template is internationalized, you run the following command:

    >>> $ ./manage.py inline_makemessages


This extracts both **inline_trans** and **trans** messages from the templates, and incorporates them to the gettext catalogs, just as makemessages does for **trans** messages.

Afterwords, you can start your server, navigate to the rendered pages (as a staff member), and, as explained above, translate the messages through the web.

