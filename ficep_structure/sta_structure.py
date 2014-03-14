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
##############################################################################'''
from openerp.osv import orm, fields


class sta_power_level(orm.Model):

    _name = 'sta.power.level'
    _inherit = ['abstract.power.level']
    _description = "State Power Level"

    _columns = {
        'assembly_category_ids': fields.one2many('sta.assembly.category', 'power_level_id',
                                                  'Assembly Categories', domain=[('active', '=', True)]),
        'instance_ids': fields.one2many('sta.instance', 'power_level_id', 'State Instances', domain=[('active', '=', True)]),
        'legislature_ids': fields.one2many('legislature', 'power_level_id', 'Legislatures', domain=[('active', '=', True)]),
        }


class sta_assembly_category(orm.Model):

    _name = 'sta.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = "State Assembly Category"

    _columns = {
        'power_level_id': fields.many2one('sta.power.level', 'State Power Level', required=True, ondelete='cascade'),
        'assembly_ids': fields.one2many('sta.assembly', 'assembly_category_id', 'State Assemblies', domain=[('active', '=', True)]),
        }


class sta_instance(orm.Model):

    _name = 'sta.instance'
    _inherit = ['abstract.instance']
    _description = "State Instance"

    def get_linked_electoral_districts(self, cr, uid, ids, context=None):
        """
        ============================
        get_linked_electoral_districts
        ============================
        Return electoral districts ids linked to sta_instance ids
        :rparam: sta_instance_ids
        :rtype: list of ids
        """
        sta_instances = self.read(cr, uid, ids, ['electoral_district_ids'], context=context)
        res_ids = []
        for sta_instance in sta_instances:
            res_ids += sta_instance['electoral_district_ids']
        return list(set(res_ids))

    _columns = {
        'parent_id': fields.many2one('sta.instance', 'Parent State Instance', select=True, ondelete='cascade'),
        'secondary_parent_id': fields.many2one('sta.instance', 'Secondary Parent State Instance', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('sta.instance', 'parent_id', string='Child State Instance'),
        'power_level_id': fields.many2one('sta.power.level', 'State Power Level', required=True, ondelete='cascade'),
        'assembly_ids': fields.one2many('sta.assembly', 'instance_id', 'State Assemblies', domain=[('active', '=', True)]),
        'electoral_district_ids': fields.one2many('electoral.district', 'sta_instance_id', 'Electoral Districts', domain=[('active', '=', True)]),
        'int_instance_id': fields.many2one('int.instance', 'Internal Instance', select=True, ondelete='cascade'),
        }


class legislature(orm.Model):

    _name = 'legislature'
    _description = "Legislature"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=128, translate=True, select=True),
        'create_date': fields.datetime('Creation Date', readonly=True),
        'deadline_date': fields.datetime('Deadline Date'),
        'expire_date': fields.datetime('Expiration Date', readonly=True, track_visibility='onchange'),
        'power_level_id': fields.many2one('sta.power.level', 'Power Level', required=True, ondelete='cascade'),
        'active': fields.boolean('Active', readonly=True),
        }

    _defaults = {
        'active': True,
    }


class sta_assembly(orm.Model):

    _name = 'sta.assembly'
    _inherit = ['abstract.assembly']
    _description = "State Assembly"

    _columns = {
        'assembly_category_id': fields.many2one('sta.assembly.category', 'Category',
                                                 required=True, ondelete='cascade'),
        'instance_id': fields.many2one('sta.instance', 'Instance',
                                                 required=True, ondelete='cascade'),
        'electoral_district_ids': fields.one2many('electoral.district', 'assembly_id', 'Electoral Districts', domain=[('active', '=', True)]),
        'designation_int_power_level_id': fields.many2one('int.power.level', string='Designation Power Level',
                                                 required=True, ondelete='cascade', readonly=False),
        }
