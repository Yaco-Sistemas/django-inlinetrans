0.5.0 (2013-09-13)
------------------

- Django 1.5 (1.4, 1.3 and 1.2) compatible, before does not work because csrf token protection
- Python 3 compatible
- Use the statics file, django-inlinetrans used media files still
- Remove polib frozen, now this is a dependence
- Remove code of inline_makemessages, now fix the problem with monkey patching
- Now we can customize with a setting that users can inline translate
- Add example project
- Add meta info

0.4.12 (2011-05-23)
-------------------

- Drop line break from inlinetrans template

0.4.11 (2011-05-17)
-------------------

- Do not try to log server restarts if the log file doesn't exist
- Fix double translation problem when template nodes are cached

0.4.10 (2011-04-18)
-------------------

- Django 1.3 compatibility

0.4.9 (2011-04-13)
------------------

- Escape msgid so the DOM parser do not replace html entities. This fixes the translation of strings with entities like &copy;

0.4.8 (2011-04-13)
------------------

- Send some data to avoid that a proxy/gateway/firewall blocks the POST request if it has no body.

0.4.7 (2011-03-22)
------------------

- Set the locale path, needed if the django server has been launched from outside the project dir.

0.4.6 (2011-03-18)
------------------

- Fixed translation when the label was found in two or more catalogs. The priority was not calculated well.

0.4.5 (2011-03-17)
------------------

- Corrected command execution in some environments.

0.4.4 (2011-03-17)
------------------

- Support for custom restart commands with parameters.

0.4.3 (2011-03-14)
------------------

- Spanish translations.

0.4.2 (2011-03-09)
------------------

- ``inline_makemessages`` command was not finding any ``itrans`` templatetag.

0.4.1 (2011-02-27)
------------------

- Fixed a bug created in 0.4.0 for anonymous user.
- Make customizable the media base directory used by inlinetrans.

0.4.0 (2011-02-24)
------------------

- Make compatible with Django 1.2 and 1.3.
- Allow using filters with the inline_trans tag.

0.3.2 (2011-02-22)
------------------

- Allow to create/update po files when the msgid is not found in any catalog.

0.3.1 (2011-02-08)
------------------

- Passed request to context because may be needed for external applications which customize templates.

0.3 (2011-02-07)
----------------

- Refactored code to be more reusable and customizable from javascript. It's now more like a jquery plugin.

0.2 (2011-01-28)
----------------

- Created itrans templatetag, an alias for inline_trans.

0.1 (2010-12-21)
----------------

- Adapting to use a egg using basic_package skel

