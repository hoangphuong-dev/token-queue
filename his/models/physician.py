# -*- coding: utf-8 -*-

from odoo import fields, models
IR_ACTIONS = "ir.actions.actions"


class Physician(models.Model):
    _inherit = 'his.physician'

    def _phy_rec_count(self):
        treatment = self.env['his.treatment']
        prescription = self.env['prescription.order']
        patient = self.env['his.patient']
        for record in self.with_context(active_test=False):
            record.treatment_count = treatment.search_count([('physician_id', '=', record.id)])
            record.appointment_count = len(record.appointment_ids)
            record.prescription_count = prescription.search_count([('physician_id', '=', record.id)])
            record.patient_count = patient.search_count(
                ['|', ('primary_physician_id', '=', record.id), ('assignee_ids', 'in', record.partner_id.id)])
            record.medicament_group_count = len(record.medicament_group_ids)

    consultation_service_id = fields.Many2one('product.product', ondelete='restrict', string='Consultation Service')
    followup_service_id = fields.Many2one('product.product', ondelete='restrict', string='Followup Service')
    appointment_duration = fields.Float('Default Consultation Duration', default=0.25)

    is_primary_surgeon = fields.Boolean(string='Primary Surgeon')
    hr_presence_state = fields.Selection(related='user_id.employee_id.hr_presence_state')
    appointment_ids = fields.One2many("his.appointment", "physician_id", "Appointments")
    appointment_count = fields.Integer(compute='_phy_rec_count', string='# Appointment')

    medicament_group_ids = fields.One2many("medicament.group", "physician_id", "Medicaments Groups")
    medicament_group_count = fields.Integer(compute='_phy_rec_count', string='#Medicaments Groups')

    treatment_count = fields.Integer(compute='_phy_rec_count', string='# Treatments')
    prescription_count = fields.Integer(compute='_phy_rec_count', string='# Prescriptions')
    patient_count = fields.Integer(compute='_phy_rec_count', string='# Patients')

    def action_treatment(self):
        action = self.env[IR_ACTIONS]._for_xml_id("his.clinic_action_form_hospital_treatment")
        action['domain'] = [('physician_id', '=', self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_appointment(self):
        action = self.env[IR_ACTIONS]._for_xml_id("his.action_appointment")
        action['domain'] = [('physician_id', '=', self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_prescription(self):
        action = self.env[IR_ACTIONS]._for_xml_id("his.act_open_his_prescription_order_view")
        action['domain'] = [('physician_id', '=', self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_patients(self):
        action = self.env[IR_ACTIONS]._for_xml_id("his_base.action_patient")
        action['domain'] = ['|', ('primary_physician_id', '=', self.id), ('assignee_ids', 'in', self.partner_id.id)]
        return action

    def action_view_medicament_groups(self):
        action = self.env[IR_ACTIONS]._for_xml_id("his.act_open_medicament_group_view")
        action['domain'] = [('physician_id', '=', self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
