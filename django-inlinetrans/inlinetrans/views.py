import os
import datetime

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.translation import get_language, ugettext as _
import inlinetrans

from inlinetrans.management.commands.inline_makemessages import make_messages
from inlinetrans.polib import pofile
from inlinetrans.utils import validate_format, find_pos
from inlinetrans.settings import get_auto_reload_method, get_auto_reload_log, get_auto_reload_time


def set_new_translation(request):
    """
    Post to include a new translation for a msgid
    """

    if not request.user.is_staff:
        return HttpResponseForbidden(_('You have no permission to update translation catalogs'))
    if not request.POST:
        return HttpResponseBadRequest(render_to_response('inlinetrans/response.html',
                                      {'message': _('Invalid request method')},
                                      context_instance=RequestContext(request)))
    else:
        result = {'errors': True,
                  'question': False,
                  'message': _('Unknow error'),
                 }
        selected_pofile = None
        msgid = smart_str(request.POST['msgid'])
        msgstr = smart_str(request.POST['msgstr'])
        retry = smart_str(request.POST['retry'])
        lang = get_language()

        # We try to update the catalog
        if retry != 'false':
            root_path = os.path.dirname(os.path.normpath(os.sys.modules[settings.SETTINGS_MODULE].__file__))
            make_messages(lang, extensions=['.html'], root_path=root_path)

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
            # We can not find the msgid in any of the catalogs
            if not selected_pofile:
                result['message'] = _('"%(msgid)s" not found in any catalog' % {'msgid': msgid})
                if retry == 'false':
                    result['question'] = _('Do you want to update the catalog (this could take longer) and try again?')
                return HttpResponse(simplejson.dumps(result), mimetype='text/plain')

            format_errors = validate_format(selected_pofile)
            if format_errors:
                result['message'] = format_errors
                return HttpResponse(simplejson.dumps(result), mimetype='text/plain')

            if poentry and not format_errors:
                try:
                    selected_pofile.metadata['Last-Translator'] = smart_str("%s %s <%s>" % (request.user.first_name, request.user.last_name, request.user.email))
                    selected_pofile.metadata['X-Translated-Using'] = smart_str("inlinetrans %s" % inlinetrans.get_version(False))
                    selected_pofile.metadata['PO-Revision-Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M%z')
                except UnicodeDecodeError:
                    pass
                selected_pofile.save()
                selected_pofile.save_as_mofile(po_filename.replace('.po', '.mo'))
                result['errors'] = False
                result['message'] = _('Catalog updated successfully')
            elif not poentry:
                result['message'] = _('PO entry not found')
    return HttpResponse(simplejson.dumps(result), mimetype='text/plain')


def inline_demo(request):
    """
    """
    return render_to_response('inlinetrans/inline_demo.html',
                              {'INLINETRANS_MEDIA_URL': settings.MEDIA_URL + 'inlinetrans/'},
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
            script = ' '.join(reload_method.split(" ")[1:])
            command = "%s &" % script
        os.system("sleep 2 && %s &> %s & " % (command, reload_log))

        return render_to_response('inlinetrans/response.html',
                                  {'message': reload_time},
                                  context_instance=RequestContext(request))

#    return HttpResponseRedirect(request.environ['HTTP_REFERER'])
