# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager

__name__ = "Truncate Table thesaurus and thesaurus_term"


def migrate(cr, version):
    if not version:
        return

    registry = RegistryManager.get(cr.dbname)
    thesaurus_obj = registry['thesaurus']
    thesaurus_term_obj = registry['thesaurus.term']
    thesaurus_term_ids = thesaurus_term_obj.search(cr, SUPERUSER_ID, [])
    thesaurus_term_obj.unlink(cr, SUPERUSER_ID, thesaurus_term_ids)
    thesaurus_ids = thesaurus_obj.search(cr, SUPERUSER_ID, [])
    thesaurus_term_obj.unlink(cr, SUPERUSER_ID, thesaurus_ids)
