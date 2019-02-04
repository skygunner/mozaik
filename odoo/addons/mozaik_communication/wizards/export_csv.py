# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv
import base64
from io import StringIO
from psycopg2.extensions import AsIs
from odoo import api, exceptions, models, fields, _


class ExportCsv(models.TransientModel):
    _name = 'export.csv'
    _description = 'Export CSV Wizard'

    export_file = fields.Binary(
        string="CSV",
        readonly=True,
    )
    export_filename = fields.Char(
        string="Export CSV filename",
    )

    @api.model
    def _get_select(self):
        return """SELECT
                 p.identifier,
                 p.name,
                 p.lastname,
                 p.firstname,
                 p.usual_lastname,
                 p.usual_firstname,
                 p.birthdate_date,
                 p.gender,
                 p.lang,
                 p.website,
                 p.secondary_website,
                 p.technical_name,
                 p.local_voluntary,
                 p.regional_voluntary,
                 p.national_voluntary,
                 p.local_only,
                 CASE
                    WHEN cc.line IS NOT NULL
                    THEN cc.line
                    ELSE p.printable_name
                 END AS printable_name,
                 cc.id as co_residency_id,
                 cc.line2 as co_residency,
                 p.membership_state_id as state_id,
                 pc.is_main as adr_main,
                 pc.unauthorized as adr_unauthorized,
                 pc.vip as adr_vip,
                 address.street2 as street2,
                 address.street as street,
                 address.zip as final_zip,
                 address.city as city,
                 country.id as country_id,
                 country.name as country_name,
                 country.code as country_code,
                 fix.is_main as fix_main,
                 fix.unauthorized as fix_unauthorized,
                 fix.vip as fix_vip,
                 fix_phone.name as fix,
                 mobile.is_main as mobile_main,
                 mobile.unauthorized as mobile_unauthorized,
                 mobile.vip as mobile_vip,
                 mobile_phone.name as mobile,
                 fax.is_main as fax_main,
                 fax.unauthorized as fax_unauthorized,
                 fax.vip as fax_vip,
                 fax_phone.name as fax,
                 ec.is_main as email_main,
                 ec.unauthorized as email_unauthorized,
                 ec.vip as email_vip,
                 ec.email"""

    @api.model
    def _common_joins(self):
        return """

                LEFT OUTER JOIN address_address address
                ON address.id = pc.address_id

                LEFT OUTER JOIN res_country country
                ON country.id = address.country_id

                LEFT OUTER JOIN co_residency cc
                ON cc.id = pc.co_residency_id

                LEFT OUTER JOIN phone_coordinate fix
                ON fix.partner_id = p.id AND
                fix.is_main = True AND
                fix.coordinate_type= 'fix' AND
                fix.active = True

                LEFT OUTER JOIN phone_phone fix_phone
                ON fix_phone.id = fix.phone_id

                LEFT OUTER JOIN phone_coordinate mobile
                ON mobile.partner_id = p.id AND
                mobile.is_main = True AND
                mobile.coordinate_type = 'mobile' AND
                mobile.active = True

                LEFT OUTER JOIN phone_phone mobile_phone
                ON mobile_phone.id = mobile.phone_id

                LEFT OUTER JOIN phone_coordinate fax
                ON fax.partner_id = p.id AND
                fax.is_main = True AND
                fax.coordinate_type = 'fax' AND
                fax.active = True

                LEFT OUTER JOIN phone_phone fax_phone
                ON fax_phone.id = fax.phone_id"""

    @api.model
    def _from_virtual_target(self):
        query = """FROM virtual_target vt

                JOIN res_partner p
                 ON p.id = vt.partner_id

                LEFT OUTER JOIN email_coordinate ec
                 ON ec.id = vt.email_coordinate_id AND
                 ec.active = True

                LEFT OUTER JOIN postal_coordinate pc
                 ON pc.id = vt.postal_coordinate_id AND
                 pc.active = True

                %(common_join)s"""
        return query

    @api.model
    def _from_email_coordinate(self):
        query = """FROM email_coordinate ec

                JOIN res_partner p
                 ON p.id = ec.partner_id

                LEFT OUTER JOIN postal_coordinate pc
                 ON pc.partner_id = p.id AND
                 pc.is_main = True AND
                 pc.active = True

                %(common_join)s"""
        return query

    @api.model
    def _from_postal_coordinate(self):
        query = """FROM postal_coordinate pc

                JOIN res_partner p
                 ON p.id = pc.partner_id

                LEFT OUTER JOIN email_coordinate ec
                 ON ec.partner_id = p.id AND
                 ec.is_main = True AND
                 ec.active = True

                %(common_join)s"""
        return query

    @api.model
    def _get_csv_rows(self):
        """
        Get the rows (header) for the specified model.
        :return: list of str
        """
        header = [
            _('Number'),
            _('Name'),
            _('Lastname'),
            _('Firstname'),
            _('Usual Lastname'),
            _('Usual Firstname'),
            _('Co-residency Line 1'),
            _('Co-residency Line 2'),
            _('Internal Instance'),
            _('Power Level'),
            _('State'),
            _('Reference'),
            _('Birth Date'),
            _('Gender'),
            _('Language'),
            _('Main Address'),
            _('Unauthorized Address'),
            _('Vip Address'),
            _('Street2'),
            _('Street'),
            _('Zip'),
            _('City'),
            _('Country Code'),
            _('Country'),
            _('Main Phone'),
            _('Unauthorized Phone'),
            _('Vip Phone'),
            _('Phone'),
            _('Main Mobile'),
            _('Unauthorized Mobile'),
            _('Vip Mobile'),
            _('Mobile'),
            _('Main Fax'),
            _('Unauthorized Fax'),
            _('Vip Fax'),
            _('Fax'),
            _('Main Email'),
            _('Unauthorized Email'),
            _('Vip Email'),
            _('Email'),
            _('Website'),
            _('Secondary Website'),
            _('Local voluntary'),
            _('Regional voluntary'),
            _('National voluntary'),
            _('Local only'),
        ]
        return header

    @api.model
    def _get_order_by(self, order_by):
        """
        Based on the given order_by, build the order by
        :param order_by: str
        :return: str
        """
        r_order_by = "p.id"
        if order_by in ['identifier', 'technical_name']:
            r_order_by = "p.%s" % order_by
        elif order_by:
            r_order_by = "country_name, final_zip, p.technical_name"
        return r_order_by

    @api.model
    def _get_csv_values(self, values, obfuscation):
        """
        Get the values of the specified obj taking into account the VIP
        obfuscation principle
        :param values: dict
        :param obfuscation: str
        :return: list of str
        """
        keys = [
            'identifier',
            'name',
            'lastname',
            'firstname',
            'usual_lastname',
            'usual_firstname',
            'printable_name',
            'co_residency',
            'state',
            'birthdate_date',
            'gender',
            'lang',
            'adr_main',
            'adr_unauthorized',
            'adr_vip',
            'adr_vip' and obfuscation or 'street2',
            'adr_vip' and obfuscation or 'street',
            'adr_vip' and obfuscation or 'final_zip',
            'adr_vip' and obfuscation or 'city',
            'country_code',
            'country_name',
            'fix_main',
            'fix_unauthorized',
            'fix_vip',
            'fix_vip' and obfuscation or 'fix',
            'mobile_main',
            'mobile_unauthorized',
            'mobile_vip',
            'mobile_vip' and obfuscation or 'mobile',
            'fax_main',
            'fax_unauthorized',
            'fax_vip',
            'fax_vip' and obfuscation or 'fax',
            'email_main',
            'email_unauthorized',
            'email_vip',
            'email_vip' and obfuscation or 'email',
            'website',
            'secondary_website',
            'local_voluntary',
            'regional_voluntary',
            'national_voluntary',
            'local_only',
        ]
        export_values = [values.get(k, '') for k in keys]
        return export_values

    @api.model
    def _prefetch_csv_datas(self, model, model_ids):
        """
        Build the SQL query and load data to build CSV
        :param model: str
        :param model_ids: list of int
        :return: list of dict
        """
        if not model_ids:
            return
        where_query = "%(table_join)s.id IN %(model_ids)s"
        if model == 'email.coordinate':
            table_join = 'ec'
            from_sql = self._from_email_coordinate()
        elif model == 'postal.coordinate':
            table_join = 'pc'
            from_sql = self._from_postal_coordinate()
        elif model == 'virtual.target':
            table_join = 'vt'
            from_sql = self._from_virtual_target()
        else:
            raise exceptions.UserError(
                _('Model %s not supported for csv export!') % model)
        where_values = {
            'table_join': AsIs(table_join),
            'model_ids': tuple(model_ids),
        }
        where_query = self.env.cr.mogrify(where_query, where_values)
        select = self._get_select()
        from_values = {
            'common_join': AsIs(self._common_joins()),
        }
        from_sql = self.env.cr.mogrify(from_sql, from_values)
        order_by = self._get_order_by(self.env.context.get('sort_by'))
        query = "%(select)s %(from)s WHERE %(where_query)s " \
                "ORDER BY %(order_by)s"
        values = {
            'where_query': AsIs(where_query.decode()),
            'order_by': AsIs(order_by),
            'select': AsIs(select),
            'from': AsIs(from_sql.decode()),
        }
        self.env.cr.execute(query, values)
        for row in self.env.cr.dictfetchall():
            yield row

    @api.model
    def _get_csv(self, model, model_ids, group_by=False):
        """
        Build a CSV file related to a coordinate model related to model_ids
        :param model: str
        :param model_ids: list of int
        :param group_by: str
        :return: str
        """
        if not model or not model_ids:
            return ''
        vip = not self.env.user.has_group(
            'mozaik_coordinate.res_groups_coordinate_vip_reader')
        states = self.env['membership.state'].search([])
        states = {st.id: st.name for st in states}
        countries = self.env['res.country'].search([])
        countries = {cnt.id: cnt.name for cnt in countries}
        selections = self.env['res.partner'].fields_get(
            allfields=['gender', 'lang'])
        genders = {k: v for k, v in selections['gender']['selection']}
        langs = {k: v for k, v in selections['lang']['selection']}
        headers = self._get_csv_rows()
        co_residencies = []
        with StringIO() as memory_file:
            writer = csv.writer(memory_file)
            writer.writerow(headers)
            for data in self._prefetch_csv_datas(model, model_ids):
                if model == 'postal.coordinate' and group_by:
                    # when grouping by co_residency, output only one row
                    # by co_residency
                    co_id = data.get('co_residency_id')
                    if co_id and co_id in co_residencies:
                        continue
                    co_residencies.append(co_id)
                # Update data depending on others models
                data.update({
                    'state': states.get(
                        data.get('state_id'), data.get('state')),
                    'country_name': countries.get(
                        data.get('country_id'), data.get('country_name')),
                    'gender': genders.get(
                        data.get('gender'), data.get('gender')),
                    'lang': langs.get(data.get('lang'), data.get('lang')),
                })
                export_values = self._get_csv_values(data, vip)
                writer.writerow(export_values)
            csv_content = memory_file.getvalue()
        return csv_content

    @api.multi
    def export(self):
        self.ensure_one()
        context = self.env.context
        model = context.get('active_model')
        model_ids = context.get('active_ids', context.get('active_id', []))
        csv_content = self._get_csv(model, model_ids)
        self.write({
            'export_file': base64.b64encode(csv_content.encode('utf-8')),
            'export_filename': _('Extract') + '.csv',
        })
        action = self.env.ref(
            "mozaik_communication.export_csv_postal_action").read()[0]
        action.update({
            'res_id': self.id,
            'target': 'new',
        })
        return action
