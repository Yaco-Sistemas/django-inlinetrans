from django.conf import settings

import re
import sys
import os
import tempfile
import subprocess


def validate_format(pofile):
    errors = []
    handle, temp_file = tempfile.mkstemp()
    os.close(handle)
    pofile.save(temp_file)

    cmd = ['msgfmt', '--check-format', temp_file]
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode != 0:
        input_lines = open(temp_file, 'r').readlines()
        error_lines = err.strip().split('\n')
        # discard last line since it only says the number of fatal errors
        error_lines = error_lines[:-1]

        def format_error_line(line):
            parts = line.split(':')
            if len(parts) == 3:
                line_number = int(parts[1])
                text = input_lines[line_number - 1]
                return text + ': ' + parts[2]
            else:
                'Unknown error: ' + line

        errors = [format_error_line(line) for line in error_lines]

    os.unlink(temp_file)
    return errors


def find_pos(lang, include_djangos = False):
    """
    scans a couple possible repositories of gettext catalogs for the given
    language code

    """

    paths = []

    # project/app/locale
    for appname in reversed(settings.INSTALLED_APPS):
        appname = str(appname) # to avoid a fail in __import__ sentence
        p = appname.rfind('.')
        if p >= 0:
            app = getattr(__import__(appname[:p], {}, {}, [appname[p+1:]]), appname[p+1:])
        else:
            app = __import__(appname, {}, {}, [])

        apppath = os.path.join(os.path.dirname(app.__file__), 'locale')

        if os.path.isdir(apppath):
            paths.append(apppath)

    # project/locale
    parts = settings.SETTINGS_MODULE.split('.')
    project = __import__(parts[0], {}, {}, [])
    paths.append(os.path.join(os.path.dirname(project.__file__), 'locale'))

    # settings
    for localepath in settings.LOCALE_PATHS:
        if os.path.isdir(localepath):
            paths.append(localepath)

    # django/locale
    if include_djangos:
        paths.append(os.path.join(os.path.dirname(sys.modules[settings.__module__].__file__), 'locale'))

    ret = []
    rx=re.compile(r'(\w+)/../\1')
    langs = (lang, )
    if u'-' in lang:
        _l, _c = map(lambda x: x.lower(), lang.split(u'-'))
        langs += (u'%s_%s' %(_l, _c), u'%s_%s' %(_l, _c.upper()), )
    elif u'_' in lang:
        _l, _c = map(lambda x: x.lower(), lang.split(u'_'))
        langs += (u'%s-%s' %(_l, _c), u'%s-%s' %(_l, _c.upper()), )

    for path in paths:
        for lang_ in langs:
            dirname = rx.sub(r'\1', '%s/%s/LC_MESSAGES/' % (path, lang_))
            for fn in ('django.po', 'djangojs.po', ):
                if os.path.isfile(dirname+fn) and os.path.abspath((dirname+fn)) not in ret:
                    ret.append(os.path.abspath(dirname+fn))
    return ret
