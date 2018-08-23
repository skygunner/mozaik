# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAddressAddress(TransactionCase):

    _module_ns = 'mozaik_address'

    def setUp(self):
        super().setUp()

        self.model_address = self.env['address.address']

    def test_create_address(self):
        vals = {
            'country_id': self.env.ref("base.be").id,
            'zip_man': '4100',
            'city_man': 'Seraing',
            'street_man': 'Rue de Colard Trouillet',
            'number': '7',
        }
        adr = self.model_address.create(vals)
        self.assertEqual(
            adr.name,
            'Rue de Colard Trouillet 7 - 4100 Seraing',
            'Create address fails with wrong name')
        self.assertEqual(
            adr.zip, '4100', 'Create address fails with wrong zip')
        self.assertEqual(
            adr.street,
            'Rue de Colard Trouillet 7',
            'Create address fails with wrong street')

        vals = {
            'number': '7',
            'box': False,
            'sequence': 3,
        }
        adr.write(vals)
        self.assertEqual(
            adr.name,
            'Rue de Colard Trouillet 7 [3] - 4100 Seraing',
            'Update address fails with wrong name')
        self.assertEqual(
            adr.street,
            'Rue de Colard Trouillet 7',
            'Update address fails with wrong street')

        vals = {
            'country_id': self.env.ref("base.us").id,
            'zip_man': '10017',
            'city_man': 'New York',
            'street_man': 'United Nations',
        }
        adr = self.model_address.create(vals)
        self.assertEqual(
            adr.name,
            'United Nations - New York - United States',
            'Create address fails with wrong name')
        self.assertEqual(
            adr.zip,
            '10017',
            'Create address fails with wrong zip')
        self.assertEqual(
            adr.street,
            'United Nations',
            'Create address fails with wrong street')

        # test the technical name
        vals = {
            'country_id': self.env.ref("base.be").id,
            'zip_man': '4100',
            'city_man': 'Seraing',
            'street_man': 'AAAAAàéÉçùièêÈ',
            'number': '7',
        }
        adr = self.model_address.create(vals)
        self.assertTrue(
            'aaaaaaeecuieee' in adr.technical_name,
            'No Accented char and no Upper For technical name')

    def test_copy_address(self):
        adr_3 = self.env.ref('%s.address_3' % self._module_ns)
        adr_4 = self.env.ref('%s.address_4' % self._module_ns)

        # 1/ an address with a null sequence cannot be duplicated
        self.assertRaises(ValidationError, adr_3.copy)

        # 2/ otherwise copy is allowed and the sequence is increased
        adr = adr_4.copy()
        self.assertEqual(
            adr.sequence, 2, 'Copy address fails with wrong sequence')
