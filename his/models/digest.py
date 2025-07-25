# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError

GROUP_HIS_USER = 'his_base.group_his_user'
STATE_NOT_IN = "not in"  # Hằng số để tránh trùng lặp literal "not in"
TEXT_NOT_HAVE_ACCESS = "Do not have access, skip this data for user's digest email"


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_clinic_appointment_total = fields.Boolean('New Appointments')
    kpi_clinic_appointment_total_value = fields.Integer(compute='_compute_kpi_clinic_appointment_total_value')

    kpi_clinic_treatment_total = fields.Boolean('New Treatments')
    kpi_clinic_treatment_total_value = fields.Integer(compute='_compute_kpi_clinic_treatment_total_value')

    kpi_clinic_procedure_total = fields.Boolean('New Procedures')
    kpi_clinic_procedure_total_value = fields.Integer(compute='_compute_kpi_clinic_procedure_total_value')

    kpi_clinic_evaluation_total = fields.Boolean('New Evaluation')
    kpi_clinic_evaluation_total_value = fields.Integer(compute='_compute_kpi_clinic_evaluation_total_value')

    kpi_clinic_patients_total = fields.Boolean('New Patients')
    kpi_clinic_patients_total_value = fields.Integer(compute='_compute_kpi_clinic_patients_total_value')

    def _compute_kpi_clinic_appointment_total_value(self):
        if not self.env.user.has_group(GROUP_HIS_USER):
            raise AccessError(_(TEXT_NOT_HAVE_ACCESS))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            appointment = self.env['his.appointment'].search_count(
                [('company_id', '=', company.id), ('date', '>=', start), ('date', '<', end),
                 ('state', STATE_NOT_IN, ['cancel'])])
            record.kpi_clinic_appointment_total_value = appointment

    def _compute_kpi_clinic_treatment_total_value(self):
        if not self.env.user.has_group(GROUP_HIS_USER):
            raise AccessError(_(TEXT_NOT_HAVE_ACCESS))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            treatment = self.env['his.treatment'].search_count(
                [('company_id', '=', company.id), ('date', '>=', start), ('date', '<', end),
                 ('state', STATE_NOT_IN, ['cancel'])])
            record.kpi_clinic_treatment_total_value = treatment

    def _compute_kpi_clinic_procedure_total_value(self):
        if not self.env.user.has_group(GROUP_HIS_USER):
            raise AccessError(_(TEXT_NOT_HAVE_ACCESS))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            procedure = self.env['clinic.patient.procedure'].search_count(
                [('company_id', '=', company.id), ('date', '>=', start), ('date', '<', end),
                 ('state', STATE_NOT_IN, ['cancel'])])
            record.kpi_clinic_procedure_total_value = procedure

    def _compute_kpi_clinic_evaluation_total_value(self):
        if not self.env.user.has_group(GROUP_HIS_USER):
            raise AccessError(_(TEXT_NOT_HAVE_ACCESS))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            evaluation = self.env['clinic.patient.evaluation'].search_count(
                [('company_id', '=', company.id), ('date', '>=', start), ('date', '<', end),
                 ('state', STATE_NOT_IN, ['cancel'])])
            record.kpi_clinic_evaluation_total_value = evaluation

    def _compute_kpi_clinic_patients_total_value(self):
        if not self.env.user.has_group(GROUP_HIS_USER):
            raise AccessError(_(TEXT_NOT_HAVE_ACCESS))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            patient = self.env['his.patient'].search_count(
                [('company_id', '=', company.id), ('create_date', '>=', start), ('create_date', '<', end)])
            record.kpi_clinic_patients_total_value = patient

    def _compute_kpis_actions(self, company, user):
        res = super(Digest, self)._compute_kpis_actions(company, user)
        res['kpi_clinic_appointment_total'] = 'his.action_appointment&menu_id=%s' % self.env.ref(
            'his.main_menu_appointment').id
        res['kpi_clinic_treatment_total'] = 'his.clinic_action_form_hospital_treatment&menu_id=%s' % self.env.ref(
            'his.main_menu_treatment').id
        res['kpi_clinic_procedure_total'] = 'his.action_clinic_patient_procedure&menu_id=%s' % self.env.ref(
            'his.menu_clinic_patient_procedure_treatment').id
        res['kpi_clinic_evaluation_total'] = 'his.action_clinic_patient_evaluation'
        res['kpi_clinic_patients_total'] = 'his_base.action_patient&menu_id=%s' % self.env.ref(
            'his_base.main_menu_patient').id
        return res
