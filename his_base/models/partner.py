# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
HIS_PATIENT = 'his.patient'


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends('birthday', 'date_of_death')
    def _get_age(self):
        today = datetime.now()
        for rec in self:
            age = ''
            today_is_birthday = False
            if rec.birthday:
                end_data = rec.date_of_death or fields.Datetime.now()
                delta = relativedelta(end_data, rec.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(
                        " Days")
                else:
                    age = str(delta.years) + _(" Year")

                if today.strftime('%m') == rec.birthday.strftime('%m') and today.strftime(
                        '%d') == rec.birthday.strftime('%d'):
                    today_is_birthday = True

            rec.age = age
            rec.today_is_birthday = today_is_birthday

    name = fields.Char(tracking=True)
    code = fields.Char(string='Code', default='New',
                       help='Identifier provided by the Health Center.', copy=False, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')], string='Gender', default='male', tracking=True)
    birthday = fields.Date(string='Date of Birth', tracking=True)

    date_of_death = fields.Date(string='Date of Death')
    age = fields.Char(string='Age', compute='_get_age')
    today_is_birthday = fields.Boolean(string='Birthday Today', compute='_get_age')
    hospital_name = fields.Char()
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')], string='Blood Group')

    is_patient = fields.Boolean(compute='_is_patient', search='_patient_search',
                                string='Is patient', help="Check if customer is linked with patient.")
    clinic_amount_due = fields.Monetary(compute='_compute_clinic_amount_due', currency_field='currency_id')
    clinic_patient_id = fields.Many2one(HIS_PATIENT, compute='_is_patient', string='patient', readonly=True)

    def _compute_clinic_amount_due(self):
        move_line = self.env['account.move.line']
        for record in self:
            amount_due = 0
            unreconciled_aml_ids = move_line.sudo().search([('reconciled', '=', False),
                                                           ('account_id.deprecated', '=', False),
                                                           ('account_id.account_type', '=', 'asset_receivable'),
                                                           ('move_id.state', '=', 'posted'),
                                                           ('partner_id', '=', record.id),
                                                           ('company_id', '=', self.env.company.id)])
            for aml in unreconciled_aml_ids:
                amount_due += aml.amount_residual
            record.clinic_amount_due = amount_due

    def _is_patient(self):
        patient = self.env[HIS_PATIENT].sudo()
        for rec in self:
            patient = patient.sudo().search([('partner_id', '=', rec.id)], limit=1)
            rec.clinic_patient_id = patient.id if patient else False
            rec.is_patient = True if patient else False

    def _patient_search(self, operator, value):
        patients = self.env[HIS_PATIENT].sudo().search([])
        return [('id', 'in', patients.mapped('partner_id').ids)]

    def create_patient(self):
        self.ensure_one()
        patient_id = self.env[HIS_PATIENT].create({
            'partner_id': self.id,
            'name': self.name,
        })
        return patient_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
