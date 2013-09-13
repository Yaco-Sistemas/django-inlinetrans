Introduction
============

.. image:: https://badge.fury.io/py/django-inlinetrans.png
    :target: https://badge.fury.io/py/django-inlinetrans

.. image:: https://pypip.in/d/django-inlinetrans/badge.png
    :target: https://pypi.python.org/pypi/django-inlinetrans

Inlinetrans is a django application that allows the translation of django templates from the rendered html in the browser. Once you have your templates internationalized with inlinetrans, you can click on the untranslated messages in their corresponding web pages to add their translations. This can be of great help for translators, as they will be able to translate the messages right in their intended context.

Features
========

- A templatetag, **inline_trans** (or **itrans**), intended as a replacement for django's **trans**.
- A management command, **inline_makemessage**, intended as a replacement for django's **makemessages**.
- A translation bar to show translatable messages, by default visible only to *staff* members (you can change this behavior with the variable USER_CAN_TRANSLATE, add it in the settings)

To translate the messages in a web page rendered in your browser, you first find out, through the translation bar, which messages have already been translated (marked light green) and which ones lack translation (marked light red).

Then, you click on a marked message, and are prompted for its translation; on entering the text and clicking OK, the new translation is sent to the server and saved in the correct .po file.

Once you have translated all messages in a page, you can click on "apply changes" on the translation bar. This forces a restart on the server, and the reloading of the page with the translations applied.

Requirements
============

To use inlinetrans, you need:

- `Django <https://www.djangoproject.com/>`_ >= 1.0
- `jQuery <http://jquery.com/>`_ >= 1.2.6

Using inlinetrans
=================


Make sure you load inlinetrans in all templates you want to internationalize, by adding the following code::

    >>>
    {% load inlinetrans %}
    {% inlinetrans_static %}
    <div id="inlinetrans-toolbar">place holder for inlinetrans toolbar</div>
    {% inlinetrans_toolbar "inlinetrans-toolbar" %}

Then, you can use::

    >>> {% inline_trans "translate this" %}

Or::

    >>> {% itrans "translate this" %}

Instead of::

    >>> {% trans "translate this" %}

Also, you can customize the toolbar and other parameters using inlinetrans as follow::

    {% load i18n inlinetrans %}

    {% inlinetrans_media %}

    <script language="javascript">
        (function ($) {
            $(document).ready(function () {
                var messages_dict = {
                    givetranslationfor: 'Give a new translation for {0} to {{ language }}',
                    emptytranslation: "You're sending an empty translation ¿Are you sure? ",
                    reloading: "Reloading",
                    apply_changes: "Apply changes",
                    applying_changes: "Applying changes",
                    error_cant_send: "Can't send translation",
                    error_cant_restart: "Can't restart server"
                };
                var new_translation_url = "{% url inlinetrans.views.set_new_translation %}";
                var restart_url = "{% url inlinetrans.views.do_restart %}";

                var toolbar_tpl = '\
                    <div class="inlinetransContainer">\
                        <img id="changes-loading" src="{{ INLINETRANS_MEDIA_URL }}img/ajax-loader-transparent.gif"/>\
                        <span class="inlinetransActions">\
                            <span class="inlinetransAction hightlightTrans">See translatable items</span>\
                            <span class="inlinetransAction hightlightNotrans">See non translated items</span>\
                            <span class="inlinetransAction restartServer">Apply changes</span>\
                        </span>\
                    </div>';
                // init inlinetrans toolbar
                $('#{{ node_id }}').inlinetranstoolbar(toolbar_tpl, new_translation_url, restart_url, messages_dict);
            });
        })(jQuery);
    </script>

Inlinetrans adds html code to each translation, so make sure you don't use **inline_trans** tags inside html attributes, such as this::

    >>> <a href="#" alt="{% inline_trans "translate this" %}"></a>

In these cases you have to use the regular **trans** tag.

Once your template is internationalized, you run the following command::

    >>> $ ./manage.py inline_makemessages

This extracts both **inline_trans** (itrans) and **trans** messages from the templates, and incorporates them to the gettext catalogs, just as makemessages does for **trans** messages.

Afterwords, you can start your server, navigate to the rendered pages (by default, as a staff member), and, as explained above, translate the messages through the web.
