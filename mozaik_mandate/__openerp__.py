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
{
    'name': 'MOZAIK: Mandate',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_structure',
        'mozaik_duplicate',
        'mozaik_address',
        'mozaik_email',
        'mozaik_person',
    ],
    'description': """
MOZAIK Mandate
==============
""",
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/copy_mandate_wizard.xml',
        'wizard/import_candidatures_wizard.xml',
        'wizard/allow_incompatible_mandate_wizard.xml',
        'wizard/electoral_results_wizard.xml',
        'wizard/update_mandate_end_date_wizard.xml',
        'abstract_mandate_view.xml',
        'mandate_view.xml',
        'res_partner_view.xml',
        'structure_view.xml',
        'sta_mandate_workflow.xml',
        'int_mandate_workflow.xml',
        'ext_mandate_workflow.xml',
        'data/ir_cron_mandate.xml',
        'data/ir_config_parameter_data.xml'
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'sequence': 150,
    'auto_install': False,
    'installable': True,
}
