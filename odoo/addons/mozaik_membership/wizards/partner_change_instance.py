# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, exceptions, fields, models, _


class PartnerChangeInstance(models.TransientModel):
    """
    Model used to update instances of partner
    """
    _name = "partner.change.instance"
    _description = "Update instances of partner"

    change_main_address_id = fields.Many2one(
        comodel_name="change.main.address",
        string="Change address",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    actual_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Current instance",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    origin = fields.Selection(
        selection=[
            ('forced', 'Forced'),
            ('membership', 'Membership'),
        ],
        required=True,
        readonly=True,
    )
    new_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="New instance",
        ondelete="cascade",
    )
    close_subscription = fields.Boolean(
        string="Close",
        default=False,
    )
    membership_line_id = fields.Many2one(
        comodel_name="membership.line",
        string="Membership Line",
        ondelete="cascade",
        readonly=True,
    )

    @api.multi
    @api.constrains('change_main_address_id', 'partner_id', 'new_instance_id')
    def _check_wizard_partner_instance(self):
        """
        Constrain function for ensure that we have only 1 new instance for
        a defined partner (into a same wizard)
        :return:
        """
        wizards = self.mapped("change_main_address_id")
        domain = [
            ('change_main_address_id', 'in', wizards.ids),
            ('close_subscription', '=', False),
            ('new_instance_id', '!=', False),
        ]
        data = self.read_group(
            domain,
            ['change_main_address_id', 'new_instance_id', 'partner_id'],
            ['change_main_address_id', 'new_instance_id', 'partner_id'],
            lazy=False,
        )
        if any(v.get('__count', 0) > 1 for v in data):
            message = _(
                "The new instance defined by partner should be unique!")
            raise exceptions.ValidationError(message)

    @api.model
    def _build_from_partner(self, partners):
        """
        Using the given partners, build list of dict to create
        current wizard lines
        :param partners: res.partner recordset
        :return: list of dict (to use in create/write)
        """
        items = []
        lines = partners.mapped('membership_line_ids').filtered('active')
        for line in lines:
            items.append({
                'origin': 'membership',
                'partner_id': line.partner_id.id,
                'membership_line_id': line.id,
                'new_instance_id': line.int_instance_id.id,
                'actual_instance_id': line.int_instance_id.id,
            })
        other_partners = partners.filtered(
            lambda s: not s.membership_line_ids and s.force_int_instance_id)
        for partner in other_partners:
            items.append({
                'origin': 'forced',
                'partner_id': partner.id,
                'new_instance_id': partner.force_int_instance_id.id,
                'actual_instance_id': partner.force_int_instance_id.id,
            })
        return items

    @api.multi
    @api.onchange('close_subscription')
    def _onchange_close_subscription(self):
        """
        Onchange for the close_subscription field
        If the close_subscription become True, clean the new_instance_id field
        :return:
        """
        for record in self:
            if record.close_subscription:
                record.new_instance_id = False

    @api.multi
    def _execute_update(self):
        """
        Execute the update on the partner
        :return: bool
        """
        # Get lines to update:
        # - close_subscription is True
        # OR - new_instance_id != actual_instance_id
        lines = self.filtered(
            lambda l: l.close_subscription or
            l.new_instance_id != l.actual_instance_id)
        for record in lines:
            if record.origin == 'forced':
                new_instance = record.new_instance_id
                record.partner_id.write({
                    'force_int_instance_id': new_instance.id,
                })
            elif record.origin == 'membership':
                line = record.membership_line_id
                # Close the line
                from_date = fields.Date.today()
                line._close(date_to=from_date, force=True)
                if not record.close_subscription:
                    line.copy({
                        'int_instance_id': record.new_instance_id.id,
                        # Force the product because the new subscription is
                        # quite equals to the previous. It's not really a
                        # new subscription
                        'product_id': line.product_id.id,
                        'price': 0,
                        'reference': False,
                    })
        return True
