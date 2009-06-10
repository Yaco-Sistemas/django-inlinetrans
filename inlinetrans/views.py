import os
import datetime

from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.encoding import smart_str
from django.utils.translation import get_language
import inlinetrans

from inlinetrans.polib import pofile
from inlinetrans.utils import validate_format, find_pos
from inlinetrans.settings import get_auto_reload_method, get_auto_reload_log, get_auto_reload_time


def set_new_translation(request):
    """
    Post to include a new translation for a msgid
    """

    message='SOME ERRORS'
    if not request.POST:
        message='ERROR: need a msgid and msgstr on post'
    else:
        msgid = smart_str(request.POST['msgid'])
        msgstr = smart_str(request.POST['msgstr'])
        lang = get_language()
        pos = find_pos(lang, include_djangos=True)
        if pos:
            for file_po in pos:
                candidate = pofile(file_po)
                poentry = candidate.find(msgid)
                if poentry:
                    selected_pofile = candidate
                    poentry.msgstr = msgstr
                    if 'fuzzy' in poentry.flags:
                        poentry.flags.remove('fuzzy')
                    po_filename = file_po
                    break
            format_errors = validate_format(selected_pofile)
            if poentry and not format_errors:
                try:
                    selected_pofile.metadata['Last-Translator'] = smart_str("%s %s <%s>" % (request.user.first_name, request.user.last_name, request.user.email))
                    selected_pofile.metadata['X-Translated-Using'] = smart_str("inlinetrans %s" % inlinetrans.get_version(False))
                    selected_pofile.metadata['PO-Revision-Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M%z')
                except UnicodeDecodeError:
                    pass
                selected_pofile.save()
                selected_pofile.save_as_mofile(po_filename.replace('.po', '.mo'))
                message='OK'

    if message == 'OK':
        return render_to_response('inlinetrans/response.html',
                                  {'message': message},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseBadRequest(render_to_response('inlinetrans/response.html',
                                      {'message': message},
                                      context_instance=RequestContext(request)))


def inline_demo(request):
    """
    """
    return render_to_response('inlinetrans/inline_demo.html',
                              {},
                              context_instance=RequestContext(request))


def do_restart(request):
    """
    * "test" for a django instance (this do a touch over settings.py for reload)
    * "apache"
    * "httpd"
    * "wsgi"
    * "restart_script <script_path_name>"
    """
    if request.user.is_staff:
        reload_method = get_auto_reload_method()
        reload_log = get_auto_reload_log()
        reload_time = get_auto_reload_time()
        command = "echo no script"
        if reload_method == 'test':
            command = 'touch settings.py'
        ## No RedHAT or similars
        elif reload_method == 'apache2':
            command = 'sudo apache2ctl restart'
        ## RedHAT, CentOS
        elif reload_method == 'httpd':
            command = 'sudo service httpd restart'

        elif reload_method.startswith('restart_script'):
            script = reload_method.split(" ")[1]
            command = "%s &" % script
        os.system("sleep 2 && %s &> %s & " % (command, reload_log))

        return render_to_response('inlinetrans/response.html',
                                  {'message': reload_time},
                                  context_instance=RequestContext(request))

#    return HttpResponseRedirect(request.environ['HTTP_REFERER'])
