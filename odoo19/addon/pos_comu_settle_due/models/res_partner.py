import ast
import logging

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, SQL
from odoo.tools.misc import format_date, get_lang


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_all_due = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice')
    total_all_overdue = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice')
    total_due = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice')
    total_overdue = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice')
    unreconciled_aml_ids = fields.One2many(
        'account.move.line', compute='_compute_total_due', readonly=False)
    total_overdue_followup = fields.Monetary(
        compute='_compute_total_due',
        groups='account.group_account_readonly,account.group_account_invoice')

    def _get_unreconciled_aml_domain(self):
        return Domain.AND([
            Domain('reconciled', '=', False),
            Domain('account_id.account_type', 'in',
                   ('asset_receivable', 'liability_payable')),
            Domain('parent_state', '=', 'posted'),
            Domain('partner_id', 'in', self.ids),
            Domain('company_id', 'child_of', self.env.company.id),
        ])

    @api.depends('invoice_ids.line_ids.no_followup')
    @api.depends_context('company', 'allowed_company_ids')
    def _compute_total_due(self):
        due_data = defaultdict(float)
        overdue_data = defaultdict(float)
        receivable_due_data = defaultdict(float)
        receivable_overdue_data = defaultdict(float)
        receivable_overdue_followup_data = defaultdict(float)
        unreconciled_aml_ids = defaultdict(list)
        for account_type, overdue, partner, no_followup, amount_residual_sum, aml_ids in self.env['account.move.line']._read_group(
            domain=self._get_unreconciled_aml_domain(),
            groupby=['account_type', 'followup_overdue',
                     'partner_id', 'no_followup'],
            aggregates=['amount_residual:sum', 'id:array_agg'],
        ):
            if account_type == 'asset_receivable':
                unreconciled_aml_ids[partner] += aml_ids
                receivable_due_data[partner] += amount_residual_sum
                if overdue:
                    receivable_overdue_data[partner] += amount_residual_sum
                    if not no_followup:
                        receivable_overdue_followup_data[partner] += amount_residual_sum

            due_data[partner] += amount_residual_sum
            if overdue:
                overdue_data[partner] += amount_residual_sum

        for partner in self:
            partner.total_all_due = due_data.get(partner, 0.0)
            partner.total_all_overdue = overdue_data.get(partner, 0.0)
            partner.total_due = receivable_due_data.get(partner, 0.0)
            partner.total_overdue = receivable_overdue_data.get(partner, 0.0)
            partner.total_overdue_followup = receivable_overdue_followup_data.get(
                partner, 0.0)
            partner.unreconciled_aml_ids = self.env['account.move.line'].browse(
                unreconciled_aml_ids.get(partner, []))

    pos_orders_amount_due = fields.Float(
        string="Sum of customers PoS orders's due amount", compute="_compute_pos_orders_amount_due")
    invoices_amount_due = fields.Float(
        string="Sum of customers's invoice due amount", compute="_compute_invoices_amount_due")

    def _compute_pos_orders_amount_due(self):
        commercial_partner_ids = {
            p.id: p.commercial_partner_id.id for p in self}
        # Fetch the total sum of 'customer_due_total' grouped by 'commercial_partner_id'
        pos_orders = self.env['pos.order']._read_group(
            domain=[
                ('commercial_partner_id', 'in', set(
                    commercial_partner_ids.values())),
                ('state', 'in', ['paid', 'done'])
            ],
            groupby=['commercial_partner_id'],
            aggregates=['customer_due_total:sum']
        )

        due_map = {order[0].id: order[1] for order in pos_orders}
        for partner in self:
            partner.pos_orders_amount_due = due_map.get(
                commercial_partner_ids[partner.id], 0.0)

    def _compute_invoices_amount_due(self):
        commercial_partner_ids = {
            p.id: p.commercial_partner_id.id for p in self}
        # Fetch the sum of 'pos_amount_unsettled' of unpaid invoices grouped by 'commercial_partner_id'
        invoices = self.env['account.move']._read_group(
            domain=[('commercial_partner_id', 'in', set(commercial_partner_ids.values())),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ('not_paid', 'partial')),
                    ('move_type', 'in', self.env['account.move'].get_sale_types())],
            groupby=['commercial_partner_id'],
            aggregates=['pos_amount_unsettled:sum']
        )

        due_map = {inv[0].id: inv[1] for inv in invoices}
        for partner in self:
            partner.invoices_amount_due = due_map.get(
                commercial_partner_ids[partner.id], 0.0)

    def get_total_due(self, config_id):
        config = self.env['pos.config'].browse(config_id)
        pos_payments = self.env['pos.order'].search([
            ('commercial_partner_id', '=',
             self.commercial_partner_id.id), ('state', '=', 'paid'),
            ('session_id.state', '!=', 'closed')]).mapped('payment_ids')
        total_settled = sum(pos_payments.filtered_domain(
            [('payment_method_id.type', '=', 'pay_later')]).mapped('amount'))

        self_sudo = self
        group_pos_user = self.env.ref('point_of_sale.group_pos_user')
        if group_pos_user in self.env.user.all_group_ids:
            self_sudo = self.sudo()  # allow POS users without accounting rights to settle dues

        total_due = self_sudo.parent_id.total_due if self.parent_id else self_sudo.total_due
        total_due += total_settled
        if self.env.company.currency_id.id != config.currency_id.id:
            pos_currency = config.currency_id
            total_due = self.env.company.currency_id._convert(
                total_due, pos_currency, self.env.company, fields.Date.today())
        partner = self.env['res.partner']._load_pos_data_read(self, config)[0]
        partner['total_due'] = total_due
        return {
            'res.partner': [partner],
        }

    def get_all_total_due(self, config_id):
        due_amounts = []
        partners = self.exists()
        for partner in partners:
            due_amounts.append(partner.get_total_due(config_id))
        return due_amounts

    @api.model
    def _load_pos_data_fields(self, config):
        params = super()._load_pos_data_fields(config)
        if self.env.user.has_group('account.group_account_readonly') or self.env.user.has_group('account.group_account_invoice'):
            params += ['credit_limit', 'total_due', 'use_partner_credit_limit',
                       'pos_orders_amount_due', 'invoices_amount_due', 'commercial_partner_id']
        return params

    @api.model
    def _load_pos_data_read(self, records, config):
        read_records = super()._load_pos_data_read(records, config)

        if config.currency_id != self.env.company.currency_id and (self.env.user.has_group('account.group_account_readonly') or self.env.user.has_group('account.group_account_invoice')):
            for record in read_records:
                record['total_due'] = self.env.company.currency_id._convert(
                    record['total_due'], config.currency_id, self.env.company, fields.Date.today())
        return read_records

    def _compute_has_moves(self):
        super()._compute_has_moves()
        for partner in self.filtered(lambda p: not p.has_moves):
            partner.has_moves = partner.total_due != 0
