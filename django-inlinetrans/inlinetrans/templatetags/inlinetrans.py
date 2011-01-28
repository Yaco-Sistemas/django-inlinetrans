import copy

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.template import TemplateSyntaxError, TokenParser
from django.templatetags.i18n import TranslateNode
from django.utils.translation import get_language
from django.utils.translation.trans_real import catalog


register = template.Library()


def get_language_name(lang):
    for lang_code, lang_name in settings.LANGUAGES:
        if lang == lang_code:
            return lang_name


class NotTranslated(object):

    @staticmethod
    def ugettext(cadena):
        raise ValueError("not translated")

    @staticmethod
    def add_fallback(func):
        return


class InlineTranslateNode(TranslateNode):

    def render(self, context):

        if 'user' in context:
            user = context['user']
        elif 'request' in context:
            user = getattr(context.get('request'), 'user', None)
        else:
            user = None
        if not (user and user.is_staff):
            return super(InlineTranslateNode, self).render(context)

        msgid = self.value.resolve(context)
        cat = copy.copy(catalog())
        cat.add_fallback(NotTranslated)
        styles = ['translatable']
        try:
            msgstr = cat.ugettext(msgid)
        except ValueError:
            styles.append("untranslated")
            msgstr = msgid
        return render_to_string('inlinetrans/inline_trans.html',
                                {'msgid': msgid,
                                 'styles': ' '.join(styles),
                                 'value': msgstr})


def inline_trans(parser, token):

    class TranslateParser(TokenParser):

        def top(self):
            value = self.value()
            if self.more():
                if self.tag() == 'noop':
                    noop = True
                else:
                    raise TemplateSyntaxError("only option for 'trans' is 'noop'")
            else:
                noop = False
            return (value, noop)
    value, noop = TranslateParser(token.contents).top()

    return InlineTranslateNode(value, noop)

register.tag('inline_trans', inline_trans)
register.tag('itrans', inline_trans)


@register.inclusion_tag('inlinetrans/inline_header.html', takes_context=True)
def inlinetrans_media(context):
    if 'user' in context and context['user'].is_staff:
        return {'is_staff': True,
                'language': get_language_name(get_language()),
                'MEDIA_URL': settings.MEDIA_URL + 'inlinetrans/'}
    else:
        return {'is_staff': False}
