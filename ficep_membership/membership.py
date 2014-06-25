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
from datetime import date
from openerp.osv import orm, fields

from openerp.addons.ficep_address.address_address import COUNTRY_CODE

from openerp.addons.ficep_person.res_partner \
    import AVAILABLE_TONGUES, AVAILABLE_GENDERS, AVAILABLE_CIVIL_STATUS

MEMBERSHIP_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]
membership_available_states = dict(MEMBERSHIP_AVAILABLE_STATES)

MEMBERSHIP_REQUEST_TYPE = [
    ('m', 'Member'),
    ('s', 'Supporter'),
]
membership_request_type = dict(MEMBERSHIP_REQUEST_TYPE)


class membership_request(orm.Model):

    _name = 'membership.request'
    _inherit = ['abstract.ficep.model']
    _description = 'Membership Request'

    _columns = {
        'lastname': fields.char('Lastname', required=True, track_visibility='onchange'),
        'firstname': fields.char('Firstname', required=True, track_visibility='onchange'),
        'state': fields.selection(MEMBERSHIP_AVAILABLE_STATES, 'Status', required=True, track_visibility='onchange'),
        'status': fields.selection(MEMBERSHIP_REQUEST_TYPE, 'Type', required=True, track_visibility='onchange'),

        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender', select=True, track_visibility='onchange'),
        'email': fields.char('Email', track_visibility='onchange'),
        'phone': fields.char('Phone', track_visibility='onchange'),
        'mobile': fields.char('Mobile', track_visibility='onchange'),
        'day': fields.integer('Day'),
        'month': fields.integer('Month'),
        'year': fields.integer('Year'),
        'birth_date': fields.date('Birthdate', track_visibility='onchange'),

        #address

        'country_id': fields.many2one('res.country', 'Country', select=True, track_visibility='onchange'),
        'country_code': fields.related('country_id', 'code', string='Country Code', type='char'),

        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        'zip_man': fields.char(string='Zip', track_visibility='onchange'),

        'town_man': fields.char(string='Town', track_visibility='onchange'),

        'address_local_street_id': fields.many2one('address.local.street', string='Reference Street', track_visibility='onchange'),
        'street_man': fields.char(string='Street', track_visibility='onchange'),

        'street2': fields.char(string='Street2', track_visibility='onchange'),

        'number': fields.char(string='Number', track_visibility='onchange'),
        'box': fields.char(string='Box', track_visibility='onchange'),

        'interests': fields.text(string='Interests'),

        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='restrict'),
        'int_instance_id': fields.many2one('int.instance', 'Internal Instance', ondelete='restrict'),
        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        'address_local_street_id': fields.many2one('address.local.street', string='Street', track_visibility='onchange'),
        'local_street': fields.related('address_local_street_id', 'local_street', 'Local Street', type='char'),
        'address_id': fields.many2one('address.address', string='Address', track_visibility='onchange'),

        'mobile_id': fields.many2one('phone.phone', 'Mobile', ondelete='restrict'),
        'phone_id': fields.many2one('phone.phone', 'Phone', ondelete='restrict'),
    }

    _unicity_keys = 'N/A'

    _defaults = {
        'country_id': lambda self, cr, uid, c:
            self.pool.get('res.country')._country_default_get(cr, uid, COUNTRY_CODE, context=c),
        'country_code': COUNTRY_CODE,

        'state': 'draft',
    }

# view methods: onchange, button

    def onchange_country_id(self, cr, uid, ids, country_id, context=None):
        return {
            'value': {
                'country_code': self.pool.get('res.country').read(cr, uid, \
                                [country_id], ['code'], context=context)[0]['code']
                                if country_id else False,
                'address_local_zip_id': False,
                'address_local_street_id': False,
             }
        }

    def onchange_partner_component(self, cr, uid, ids, day, month, year, lastname, firstname, email, context=None):
        """
        ===================
        onchange_country_id
        ===================
        try to find a new partner_id depending of the
        birth_date, lastname, firstname, email
        """
        birth_date = self.get_birth_date(cr, uid, day, month, year, context=context)
        email = self.get_format_email(cr, uid, email, context=context)
        partner_id = self.get_partner_id(cr, uid, birth_date, firstname, lastname, email, context=context),
        return {
            'value': {
                'partner_id': partner_id,
                'birth_date': '%s' % birth_date,
                'email': email,
            }
        }

    # public method

    def get_format_email(self, cr, uid, email, context=None):
        """
        ================
        get_format_email
        ================
        Check and format email just like `email.coordinate` do it
        return email value
        """
        email_obj = self.pool['email.coordinate']
        if email_obj._check_email_format(cr, uid, email, context=context) != None:
            email = email_obj.format_email(cr, uid, email, context=context)
        return email

    def get_partner_id(self, cr, uid, birth_date, firstname, lastname, email, context=None):
        """
        ==============
        get_partner_id
        ==============
        Make special combinations of domains to try to find
        a unique partner_id
        """
        partner_obj = self.pool['virtual.custom.partner']
        partner_domains = []

        if birth_date and email:
            partner_domains.append("[('birth_date', '=', '%s'),('email', '=', '%s')]" % (birth_date, email))
        if birth_date and email and firstname and lastname:
            partner_domains.append("[('birth_date', '=', '%s'),('email', '=', '%s'),('firstname', 'ilike', '%s'), ('lastname', 'ilike', '%s')]"\
                       % (birth_date, email, firstname, lastname))
        if email:
            partner_domains.append("[('email', '=', '%s')]" % (email))
        if firstname and lastname:
            partner_domains.append("[('firstname', 'ilike', '%s'),('lastname', 'ilike', '%s')]" % (firstname, lastname))

        partner_id = False
        virtual_partner_id = self.persist_search(cr, uid, partner_obj, partner_domains, context=context)
        # because this is not a real partner but a virtual partner
        if virtual_partner_id:
            partner_id = partner_obj.read(cr, uid, [virtual_partner_id], ['partner_id'])[0]
            partner_id = partner_id['partner_id'][0]
        return partner_id

    def get_birth_date(self, cr, uid, day, month, year, context=None):
        """
        ==============
        get_birth_date
        ==============
        Return a birth date case where all parameters day/month/year
        are initialized
        """
        birth_date = False
        if day and month and year:
            birth_date = date(year, month, day)
        return birth_date

    def pre_process(self, cr, uid, vals, context=None):
        """
        ===========
        pre_process
        ===========
        * Try to create a birth_date if all the components are there. (day/month/year)
        * Next step is to find partner by different way:
        ** birth_date + email
        ** birth_date + lastname + firstname
        ** email + firstname + lastname
        ** email
        ** firstname + lastname
        * Case of partner found: search email coordinate and phone coordinate for this partner
        * Try to find street_id and zip_id

        :rparam vals: dictionary used to create ``membership_request``
        """
        if context is None:
            context = {}

        mobile_id = False
        phone_id = False
        address_id = False

        firstname = vals.get('firstname', False)
        lastname = vals.get('lastname', False)
        day = vals.get('day', False)
        month = vals.get('month', False)
        year = vals.get('year', False)
        email = vals.get('email', False)
        mobile = vals.get('mobile', False)
        phone = vals.get('phone', False)
        zip_man = vals.get('zip_man', False)
        town_man = vals.get('town_man', False)
        street_man = vals.get('street_man', False)
        gender = vals.get('gender', False)
        status = vals.get('status', False)
        interest = vals.get('interest', False)

        birth_date = self.get_birth_date(cr, uid, day, month, year, context=False)

        if mobile or phone:
            ctx = context.copy()
            ctx.update({'install_mode': True})
            phone_obj = self.pool['phone.phone']

            if mobile:
                mobile = phone_obj._check_and_format_number(cr, uid, mobile, context=ctx)
                # try to find this number into phone.phone records with type `mobile`
                mobile_ids = phone_obj.search(cr, uid, [('name', '=', mobile), ('type', '=', 'mobile')])
                mobile_id = mobile_ids and mobile_ids[0]
            if phone:
                phone = self.pool['phone.phone']._check_and_format_number(cr, uid, phone, context=ctx)
                # try to find this number into phone.phone records with type `fix`
                phone_ids = phone_obj.search(cr, uid, [('name', '=', phone), ('type', '=', 'fix')])
                phone_id = phone_ids and phone_ids[0]

        email = self.get_format_email(cr, uid, email, context=context)
        partner_id = self.get_partner_id(cr, uid, birth_date, email, firstname, lastname, context=False)

        # Find local zip code
        address_local_zip_obj = self.pool['address.local.zip']
        address_local_zip_domains = ["[('local_zip', '=', '%s')]" % zip_man,
                                     "[('local_zip', '=', '%s'),('town', '=', '%s')]" % (zip_man, town_man)]
        address_local_zip_id = self.persist_search(cr, uid, address_local_zip_obj, address_local_zip_domains, context=context)

        # find local street
        address_local_street_obj = self.pool['address.local.street']
        address_local_street_domains = ["[('local_street', '=', '%s')]" % street_man]
        if address_local_zip_id:
            address_local_street_domains.append("[('local_street','=', '%s'),('local_zip', '=', '%s')]" % (street_man, town_man))

        address_local_street_id = self.persist_search(cr, uid, address_local_street_obj, address_local_street_domains, context=context)

        #update vals dictionary because some inputs may have changed (and new values too)
        vals.update({
            'partner_id': partner_id,
            'lastname': lastname,
            'firstname': firstname,
            'gender': gender,
            'birth_date': birth_date,
            'day': day,
            'month': month,
            'year': year,

            'status': status,
            'street_man': street_man,
            'zip_man': zip_man,
            'town_man': town_man,

            'mobile': mobile,
            'phone': phone,
            'email': email,

            'mobile_id': mobile_id,
            'phone_id': phone_id,
            'address_local_zip_id': address_local_zip_id,
            'address_local_street_id': address_local_street_id,

            'interest': interest,
        })

        return vals

    def persist_search(self, cr, uid, model_obj, domains, context=None):
        """
        ==============
        persist_search
        ==============
        This method will make a search with a list of domain and return result only
        if it is a single result
        :type model_obj: model object into odoo (ex: res.partner)
        :param model_obj: used to make the research
        :type domains: []
        :param domains: contains a list of domains
        :rparam: result of the search
        """
        def rec_search(loop_counter):
            if loop_counter >= len(domains):
                return False
            else:
                model_ids = model_obj.search(cr, uid, eval(domains[loop_counter]), context=context)
                if len(model_ids) == 1:
                    return model_ids[0]
                else:
                    return rec_search(loop_counter + 1)

        return rec_search(0)

    def confirm_request(self, cr, uid, ids, context=None):
        pass

    def cancel_request(self, cr, uid, ids, context=None):
        pass

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        Call ``pre-process`` function to prepare input values.
        """
        self.pre_process(cr, uid, vals, context=context)
        return super(membership_request, self).create(cr, uid, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
