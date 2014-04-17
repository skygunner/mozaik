# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm
from openerp.addons.ficep_mandate.wizard import import_candidatures_wizard as wizard
import tempfile
import base64

_logger = logging.getLogger(__name__)


class test_import_candidatures_wizard(SharedSetupTransactionCase):
    _data_files = (
        '../../ficep_base/tests/data/res_partner_data.xml',
        '../../ficep_structure/tests/data/structure_data.xml',
        'data/mandate_data.xml',
    )

    _module_ns = 'ficep_mandate'

    def setUp(self):
        super(test_import_candidatures_wizard, self).setUp()

    def test_import_legislative_state_candidatures(self):
        sc_conseiller_provincial_id = self.ref('%s.sc_conseiller_provincial' % self._module_ns)

        partner_paul_id = self.ref('%s.res_partner_paul' % self._module_ns)
        partner_pauline_id = self.ref('%s.res_partner_pauline' % self._module_ns)
        partner_marc_id = self.ref('%s.res_partner_marc' % self._module_ns)

        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard.file_import_structure) + '\n')
        data = [str(partner_paul_id), '', 'True', '1', 'True', '1']
        temp_file.write(','.join(data) + '\n')
        data = [str(partner_pauline_id), '', 'True', '2', 'False', '']
        temp_file.write(','.join(data) + '\n')
        data = [str(partner_marc_id), '', 'True', '3', 'True', '2']
        temp_file.write(','.join(data) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_conseiller_provincial_id],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)
        wizard_pool.validate_file(self.cr, self.uid, [wiz_id])
        wizard_pool.import_candidatures(self.cr, self.uid, [wiz_id])

        self.assertTrue(len(self.registry('sta.candidature').search(self.cr, self.uid, [('selection_committee_id', '=', sc_conseiller_provincial_id)])), 3)

    def test_import_legislative_state_candidatures_wrong_files(self):
        sc_conseiller_provincial_id = self.ref('%s.sc_conseiller_provincial' % self._module_ns)

        '''
            File with wrong structure of columns
        '''
        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        header = []
        header.extend(wizard.file_import_structure)
        header.remove('id_ecolo')
        temp_file.write(','.join(header) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_conseiller_provincial_id],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)

        self.assertRaises(orm.except_orm, wizard_pool.validate_file, self.cr, self.uid, [wiz_id])

        '''
            File with bad column in header
        '''
        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        header = []
        header.extend(wizard.file_import_structure)
        header[0] = 'bad_value'
        temp_file.write(','.join(header) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_conseiller_provincial_id],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)

        self.assertRaises(orm.except_orm, wizard_pool.validate_file, self.cr, self.uid, [wiz_id])

        '''
            File with unknown partner
        '''
        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard.file_import_structure) + '\n')
        data = [str(9999999), '', 'True', '1', 'True', '1']
        temp_file.write(','.join(data) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_conseiller_provincial_id],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)
        self.assertRaises(orm.except_orm, wizard_pool.validate_file, self.cr, self.uid, [wiz_id])

    def test_import_non_legislative_state_candidatures(self):
        sc_gouverneur = self.ref('%s.sc_gouverneur' % self._module_ns)

        partner_paul_id = self.ref('%s.res_partner_paul' % self._module_ns)

        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard.file_import_structure) + '\n')
        data = [str(partner_paul_id), '', 'False', '', 'False', '']
        temp_file.write(','.join(data) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_gouverneur],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)
        wizard_pool.validate_file(self.cr, self.uid, [wiz_id])
        wizard_pool.import_candidatures(self.cr, self.uid, [wiz_id])

        self.assertTrue(len(self.registry('sta.candidature').search(self.cr, self.uid, [('selection_committee_id', '=', sc_gouverneur)])), 1)

    def test_import_non_legislative_state_candidatures_wrong_file(self):
        sc_gouverneur = self.ref('%s.sc_gouverneur' % self._module_ns)

        partner_paul_id = self.ref('%s.res_partner_paul' % self._module_ns)

        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard.file_import_structure) + '\n')
        data = [str(partner_paul_id), '', 'True', '', 'False', '']
        temp_file.write(','.join(data) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_gouverneur],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)

        self.assertRaises(orm.except_orm, wizard_pool.validate_file, self.cr, self.uid, [wiz_id])

        temp_file = tempfile.SpooledTemporaryFile(mode='w+r')
        temp_file.write(','.join(wizard.file_import_structure) + '\n')
        data = [str(partner_paul_id), '', 'False', '', 'True', '']
        temp_file.write(','.join(data) + '\n')
        temp_file.seek(0)
        data_file = temp_file.read()
        temp_file.close()

        context = {
            'active_ids': [sc_gouverneur],
            'active_model': 'selection.committee',
        }
        wizard_pool = self.registry('import.candidatures.wizard')
        wiz_id = wizard_pool.create(self.cr, self.uid, {'source_file': base64.encodestring(data_file)}, context=context)

        self.assertRaises(orm.except_orm, wizard_pool.validate_file, self.cr, self.uid, [wiz_id])
