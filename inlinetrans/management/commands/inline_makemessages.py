import re

from django.core.management.commands import makemessages
from django.utils.translation import trans_real


class Command(makemessages.Command):

    def handle(self, *args, **options):
        new_patthern = trans_real.inline_re.pattern.replace('trans', '(?:trans|inline_trans|itrans)')
        trans_real.inline_re = re.compile(new_patthern)
        return super(Command, self).handle(*args, **options)
