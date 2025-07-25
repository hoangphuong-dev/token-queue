# -*- coding: utf-8 -*-
# Part of Mate See LICENSE file for full copyright and licensing details.

from odoo import fields, models
PRODUCT_PRODUCT = "product.product"
STOCK_LOCATION = "stock.location"


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    patient_registration_product_id = fields.Many2one(PRODUCT_PRODUCT,
                                                      related='company_id.patient_registration_product_id',
                                                      domain=[('type', '=', 'service')],
                                                      string='Patient Registration Invoice Product',
                                                      ondelete='cascade', help='Registration Product', readonly=False)
    treatment_registration_product_id = fields.Many2one(PRODUCT_PRODUCT,
                                                        related='company_id.treatment_registration_product_id',
                                                        domain=[('type', '=', 'service')],
                                                        string='Treatment Registration Invoice Product',
                                                        ondelete='cascade', help='Registration Product', readonly=False)
    consultation_product_id = fields.Many2one(PRODUCT_PRODUCT,
                                              related='company_id.consultation_product_id',
                                              domain=[('type', '=', 'service')],
                                              string='Consultation Invoice Product',
                                              ondelete='cascade', help='Consultation Product', readonly=False)
    followup_days = fields.Float(related='company_id.followup_days', string='Followup Days', readonly=False)
    followup_product_id = fields.Many2one(PRODUCT_PRODUCT,
                                          related='company_id.followup_product_id',
                                          domain=[('type', '=', 'service')],
                                          string='Follow-up Invoice Product',
                                          ondelete='cascade', help='Followup Product', readonly=False)
    clinic_followup_activity_type_id = fields.Many2one('mail.activity.type',
                                                       related='company_id.clinic_followup_activity_type_id',
                                                       string='Follow-up Activity Type',
                                                       ondelete='cascade', help='Followup Activity Type',
                                                       readonly=False)
    registration_date = fields.Char(related='company_id.registration_date', string='Date of Registration',
                                    readonly=False)
    appointment_invoice_policy = fields.Selection(related='company_id.appointment_invoice_policy',
                                                  string="Appointment Invoicing Policy", readonly=False)
    clinic_check_appo_payment = fields.Boolean(related='company_id.clinic_check_appo_payment',
                                               string="Check Appointment Payment Status before Accepting Request",
                                               readonly=False)
    clinic_appointment_planned_duration = fields.Float(related='company_id.clinic_appointment_planned_duration',
                                                       string='Default Appointment Planned Duration', readonly=False)
    appointment_usage_location_id = fields.Many2one(STOCK_LOCATION,
                                                    related='company_id.appointment_usage_location_id',
                                                    domain=[('usage', '=', 'customer')],
                                                    string='Usage Location for Consumed Products in Appointment',
                                                    readonly=False)
    appointment_stock_location_id = fields.Many2one(STOCK_LOCATION,
                                                    related='company_id.appointment_stock_location_id',
                                                    domain=[('usage', '=', 'internal')],
                                                    string='Stock Location for Consumed Products in Appointment',
                                                    readonly=False)

    procedure_usage_location_id = fields.Many2one(STOCK_LOCATION,
                                                  related='company_id.procedure_usage_location_id',
                                                  domain=[('usage', '=', 'customer')],
                                                  string='Usage Location for Consumed Products in Procedure',
                                                  readonly=False)
    procedure_stock_location_id = fields.Many2one(STOCK_LOCATION,
                                                  related='company_id.procedure_stock_location_id',
                                                  domain=[('usage', '=', 'internal')],
                                                  string='Stock Location for Consumed Products in Procedure',
                                                  readonly=False)

    group_patient_registration_invoicing = fields.Boolean("Patient Registration Invoicing",
                                                          implied_group='his.group_patient_registration_invoicing')
    group_treatment_invoicing = fields.Boolean("Treatment Invoicing", implied_group='his.group_treatment_invoicing')
    clinic_prescription_qrcode = fields.Boolean(related='company_id.clinic_prescription_qrcode',
                                                string="Print Authentication QrCode on Prescription", readonly=False)
    auto_followup_days = fields.Float(related='company_id.auto_followup_days', string='Default Followup on (Days)',
                                      readonly=False)
    patient_weight_measure_uom = fields.Char(string='Patient Weight unit of measure',
                                             config_parameter='his.clinic_patient_weight_uom')
    patient_height_measure_uom = fields.Char(string='Patient Height unit of measure',
                                             config_parameter='his.clinic_patient_height_uom')
    patient_temp_measure_uom = fields.Char(string='Patient Temp unit of measure',
                                           config_parameter='his.clinic_patient_temp_uom')
    patient_spo2_measure_uom = fields.Char(string='Patient SpO2 unit of measure',
                                           config_parameter='his.clinic_patient_spo2_uom')
    patient_rbs_measure_uom = fields.Char(string='Patient RBS unit of measure',
                                          config_parameter='his.clinic_patient_rbs_uom')
    patient_head_circum_measure_uom = fields.Char(string='Patient Head Circumference unit of measure',
                                                  config_parameter='his.clinic_patient_head_circum_uom')
    clinic_cancel_old_appointment = fields.Boolean(string='Cancel Old Appointment',
                                                   related='company_id.clinic_cancel_old_appointment', readonly=False)
    clinic_auto_appo_confirmation_mail = fields.Boolean(string="Send Appointment Confirmation Mail",
                                                        related='company_id.clinic_auto_appo_confirmation_mail',
                                                        readonly=False)

    clinic_reminder_day = fields.Float(related='company_id.clinic_reminder_day', string="Reminder Days", readonly=False)
    clinic_reminder_hours = fields.Float(related='company_id.clinic_reminder_hours', string="Reminder Hours",
                                         readonly=False)
    clinic_flag_days = fields.Integer(related='company_id.clinic_flag_days', string="Warning Flag Days",
                                      help="Days to count cancelled appointment", readonly=False)
    clinic_flag_count_limit = fields.Integer(related='company_id.clinic_flag_count_limit',
                                             string="Count Limit for Flag",
                                             help="Configure number to show alert flag after couting that many cancelled appointments",
                                             readonly=False)
