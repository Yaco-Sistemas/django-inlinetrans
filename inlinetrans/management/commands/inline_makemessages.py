# Copy from django/core/management/commands/makemessages.py
#   and mixing from django/utils/translation/trans_reals.py
#   Modified inline_re and groups to get words

import re
import os
import sys
import warnings
from itertools import dropwhile
from optparse import make_option

from django.core.management.base import CommandError, BaseCommand

try:
    set
except NameError:
    from sets import Set as set     # For Python 2.3

# Intentionally silence DeprecationWarnings about os.popen3 in Python 2.6. It's
# still sensible for us to use it, since subprocess didn't exist in 2.3.
warnings.filterwarnings('ignore', category=DeprecationWarning, message=r'os\.popen3')

pythonize_re = re.compile(r'\n\s*//')


from django.utils.translation.trans_real import *

inline_re = re.compile(r"""^\s*(inline_trans|trans|itrans)\s+((?:".*?")|(?:'.*?'))\s*""")


def templatize(src):
    """
    Turns a Django template into something that is understood by xgettext. It
    does so by translating the Django translation tags into standard gettext
    function invocations.
    """
    from django.template import Lexer, TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK
    out = StringIO()
    intrans = False
    inplural = False
    singular = []
    plural = []
    for t in Lexer(src, None).tokenize():
        if intrans:
            if t.token_type == TOKEN_BLOCK:
                endbmatch = endblock_re.match(t.contents)
                pluralmatch = plural_re.match(t.contents)
                if endbmatch:
                    if inplural:
                        out.write(' ngettext(%r,%r,count) ' % (''.join(singular), ''.join(plural)))
                        for part in singular:
                            out.write(blankout(part, 'S'))
                        for part in plural:
                            out.write(blankout(part, 'P'))
                    else:
                        out.write(' gettext(%r) ' % ''.join(singular))
                        for part in singular:
                            out.write(blankout(part, 'S'))
                    intrans = False
                    inplural = False
                    singular = []
                    plural = []
                elif pluralmatch:
                    inplural = True
                else:
                    raise SyntaxError("Translation blocks must not include other block tags: %s" % t.contents)
            elif t.token_type == TOKEN_VAR:
                if inplural:
                    plural.append('%%(%s)s' % t.contents)
                else:
                    singular.append('%%(%s)s' % t.contents)
            elif t.token_type == TOKEN_TEXT:
                if inplural:
                    plural.append(t.contents)
                else:
                    singular.append(t.contents)
        else:
            if t.token_type == TOKEN_BLOCK:
                imatch = inline_re.match(t.contents)
                bmatch = block_re.match(t.contents)
                cmatches = constant_re.findall(t.contents)
                if imatch:
                    # Modified group for new inline_re syntax
                    g = imatch.group(2)
                    if g[0] == '"': g = g.strip('"')
                    elif g[0] == "'": g = g.strip("'")
                    out.write(' gettext(%r) ' % g)
                elif bmatch:
                    for fmatch in constant_re.findall(t.contents):
                        out.write(' _(%s) ' % fmatch)
                    intrans = True
                    inplural = False
                    singular = []
                    plural = []
                elif cmatches:
                    for cmatch in cmatches:
                        out.write(' _(%s) ' % cmatch)
                else:
                    out.write(blankout(t.contents, 'B'))
            elif t.token_type == TOKEN_VAR:
                parts = t.contents.split('|')
                cmatch = constant_re.match(parts[0])
                if cmatch:
                    out.write(' _(%s) ' % cmatch.group(1))
                for p in parts[1:]:
                    if p.find(':_(') >= 0:
                        out.write(' %s ' % p.split(':',1)[1])
                    else:
                        out.write(blankout(p, 'F'))
            else:
                out.write(blankout(t.contents, 'X'))
    return out.getvalue()


def handle_extensions(extensions=('html',)):
    """
    organizes multiple extensions that are separated with commas or passed by
    using --extension/-e multiple times.

    for example: running 'django-admin makemessages -e js,txt -e xhtml -a'
    would result in a extension list: ['.js', '.txt', '.xhtml']

    >>> handle_extensions(['.html', 'html,js,py,py,py,.py', 'py,.py'])
    ['.html', '.js']
    >>> handle_extensions(['.html, txt,.tpl'])
    ['.html', '.tpl', '.txt']
    """
    ext_list = []
    for ext in extensions:
        ext_list.extend(ext.replace(' ','').split(','))
    for i, ext in enumerate(ext_list):
        if not ext.startswith('.'):
            ext_list[i] = '.%s' % ext_list[i]

    # we don't want *.py files here because of the way non-*.py files
    # are handled in make_messages() (they are copied to file.ext.py files to
    # trick xgettext to parse them as Python files)
    return set([x for x in ext_list if x != '.py'])

def make_messages(locale=None, domain='django', verbosity='1', all=False, extensions=None, locale_path=None, root_path=None):
    """
    Uses the locale directory from the Django SVN tree or an application/
    project to process all
    """
    # Need to ensure that the i18n framework is enabled
    from django.conf import settings
    if settings.configured:
        settings.USE_I18N = True
    else:
        settings.configure(USE_I18N = True)


    if locale_path and os.path.isdir(locale_path):
        localedir = locale_path
    elif os.path.isdir(os.path.join('conf', 'locale')):
        localedir = os.path.abspath(os.path.join('conf', 'locale'))
    elif os.path.isdir('locale'):
        localedir = os.path.abspath('locale')
    else:
        raise CommandError("This script should be run from the Django SVN tree or your project or app tree. If you did indeed run it from the SVN checkout or your project or application, maybe you are just missing the conf/locale (in the django tree) or locale (for project and application) directory? It is not created automatically, you have to create it by hand if you want to enable i18n for your project or application.")

    if domain not in ('django', 'djangojs'):
        raise CommandError("currently makemessages only supports domains 'django' and 'djangojs'")

    if (locale is None and not all) or domain is None:
        # backwards compatible error message
        if not sys.argv[0].endswith("make-messages.py"):
            message = "Type '%s help %s' for usage.\n" % (os.path.basename(sys.argv[0]), sys.argv[1])
        else:
            message = "usage: make-messages.py -l <language>\n   or: make-messages.py -a\n"
        raise CommandError(message)

    # xgettext versions prior to 0.15 assumed Python source files were encoded
    # in iso-8859-1, and produce utf-8 output.  In the case where xgettext is
    # given utf-8 input (required for Django files with non-ASCII characters),
    # this results in a utf-8 re-encoding of the original utf-8 that needs to be
    # undone to restore the original utf-8.  So we check the xgettext version
    # here once and set a flag to remember if a utf-8 decoding needs to be done
    # on xgettext's output for Python files.  We default to assuming this isn't
    # necessary if we run into any trouble determining the version.
    xgettext_reencodes_utf8 = False
    (stdin, stdout, stderr) = os.popen3('xgettext --version', 't')
    match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', stdout.read())
    if match:
        xversion = (int(match.group('major')), int(match.group('minor')))
        if xversion < (0, 15):
            xgettext_reencodes_utf8 = True
 
    languages = []
    if locale is not None:
        languages.append(locale)
    elif all:
        languages = [el for el in os.listdir(localedir) if not el.startswith('.')]

    for locale in languages:
        if verbosity > 0:
            print "processing language", locale
        basedir = os.path.join(localedir, locale, 'LC_MESSAGES')
        if not os.path.isdir(basedir):
            os.makedirs(basedir)

        pofile = os.path.join(basedir, '%s.po' % domain)
        potfile = os.path.join(basedir, '%s.pot' % domain)

        if os.path.exists(potfile):
            os.unlink(potfile)

        all_files = []
        for (dirpath, dirnames, filenames) in os.walk(root_path):
            for d in dirnames:
                fulldir = os.path.join(dirpath, d)
                if os.path.islink(fulldir) and os.path.exists(fulldir):
                    dirnames[dirnames.index(d)]=os.path.realpath(fulldir)
            all_files.extend([(dirpath, f) for f in filenames])
        all_files.sort()
        for dirpath, file in all_files:
            file_base, file_ext = os.path.splitext(file)
            if domain == 'djangojs' and file_ext == '.js':
                if verbosity > 1:
                    sys.stdout.write('processing file %s in %s\n' % (file, dirpath))
                src = open(os.path.join(dirpath, file), "rU").read()
                src = pythonize_re.sub('\n#', src)
                thefile = '%s.py' % file
                open(os.path.join(dirpath, thefile), "w").write(src)
                cmd = 'xgettext -d %s -L Perl --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --from-code UTF-8 -o - "%s"' % (domain, os.path.join(dirpath, thefile))
                (stdin, stdout, stderr) = os.popen3(cmd, 't')
                msgs = stdout.read()
                errors = stderr.read()
                if errors:
                    raise CommandError("errors happened while running xgettext on %s\n%s" % (file, errors))
                old = '#: '+os.path.join(dirpath, thefile)[2:]
                new = '#: '+os.path.join(dirpath, file)[2:]
                msgs = msgs.replace(old, new)
                if os.path.exists(potfile):
                    # Strip the header
                    msgs = '\n'.join(dropwhile(len, msgs.split('\n')))
                else:
                    msgs = msgs.replace('charset=CHARSET', 'charset=UTF-8')
                if msgs:
                    open(potfile, 'ab').write(msgs)
                os.unlink(os.path.join(dirpath, thefile))
            elif domain == 'django' and (file_ext == '.py' or file_ext in extensions):
                thefile = file
                if file_ext in extensions:
                    src = open(os.path.join(dirpath, file), "rU").read()
                    thefile = '%s.py' % file
                    open(os.path.join(dirpath, thefile), "w").write(templatize(src))
                if verbosity > 1:
                    sys.stdout.write('processing file %s in %s\n' % (file, dirpath))
                cmd = 'xgettext -d %s -L Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --keyword=ugettext_noop --keyword=ugettext_lazy --keyword=ungettext_lazy:1,2 --from-code UTF-8 -o - "%s"' % (
                    domain, os.path.join(dirpath, thefile))
                (stdin, stdout, stderr) = os.popen3(cmd, 't')
                msgs = stdout.read()
                errors = stderr.read()
                if errors:
                    raise CommandError("errors happened while running xgettext on %s\n%s" % (file, errors))

                if xgettext_reencodes_utf8:
                    msgs = msgs.decode('utf-8').encode('iso-8859-1')

                if thefile != file:
                    old = '#: '+os.path.join(dirpath, thefile)[2:]
                    new = '#: '+os.path.join(dirpath, file)[2:]
                    msgs = msgs.replace(old, new)
                if os.path.exists(potfile):
                    # Strip the header
                    msgs = '\n'.join(dropwhile(len, msgs.split('\n')))
                else:
                    msgs = msgs.replace('charset=CHARSET', 'charset=UTF-8')
                if msgs:
                    open(potfile, 'ab').write(msgs)
                if thefile != file:
                    os.unlink(os.path.join(dirpath, thefile))

        if os.path.exists(potfile):
            (stdin, stdout, stderr) = os.popen3('msguniq --to-code=utf-8 "%s"' % potfile, 't')
            msgs = stdout.read()
            errors = stderr.read()
            if errors:
                raise CommandError("errors happened while running msguniq\n%s" % errors)
            open(potfile, 'w').write(msgs)
            if os.path.exists(pofile):
                cmd = 'msgmerge -N -q "%s" "%s"' % (pofile, potfile)
                (stdin, stdout, stderr) = os.popen3(cmd, 't')
                msgs = stdout.read()
                errors = stderr.read()
                if errors:
                    raise CommandError("errors happened while running msgmerge\n%s" % errors)
            open(pofile, 'wb').write(msgs)
            os.unlink(potfile)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--locale', '-l', default=None, dest='locale',
            help='Creates or updates the message files only for the given locale (e.g. pt_BR).'),
        make_option('--domain', '-d', default='django', dest='domain',
            help='The domain of the message files (default: "django").'),
        make_option('--all', '-a', action='store_true', dest='all',
            default=False, help='Reexamines all source code and templates for new translation strings and updates all message files for all available languages.'),
        make_option('--extension', '-e', dest='extensions',
            help='The file extension(s) to examine (default: ".html", separate multiple extensions with commas, or use -e multiple times)',
            action='append'),
        make_option('--locale-path', '-p', dest='locale-path', default=None,
            help='Path to your project locale dir. Needed only if you call the command from outside your main project directory.'),
        make_option('--root-path', '-r', dest='root-path', default='.',
            help='Root path to find files to include in catalogs.'),
    )
    help = "Runs over the entire source tree of the current directory and pulls out all strings marked for translation. It creates (or updates) a message file in the conf/locale (in the django tree) or locale (for project and application) directory."

    requires_model_validation = False
    can_import_settings = False

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")

        locale = options.get('locale')
        domain = options.get('domain')
        verbosity = int(options.get('verbosity'))
        process_all = options.get('all')
        extensions = options.get('extensions') or ['html']
        locale_path = options.get('locale-path')
        root_path = options.get('root-path')

        if domain == 'djangojs':
            extensions = []
        else:
            extensions = handle_extensions(extensions)

        if '.js' in extensions:
            raise CommandError("JavaScript files should be examined by using the special 'djangojs' domain only.")

        make_messages(locale, domain, verbosity, process_all, extensions, locale_path, root_path)
