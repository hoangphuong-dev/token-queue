# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

RES_PARNER = 'res.partner'


class FormatGOVCodeLabelMixin(models.AbstractModel):
    _name = "format.gov.code.label.mixin"
    _description = "Country Specific Gov Code Label"

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if gov_code_label := self.env.company.country_id.gov_code_label:
            for node in arch.iterfind(".//field[@name='gov_code']"):
                node.set("string", gov_code_label)
            # In some module gov_code field is replaced and so above string change is not working
            for node in arch.iterfind(".//label[@for='gov_code']"):
                node.set("string", gov_code_label)
        return arch, view


class MatePatient(models.Model):
    _name = 'his.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'format.gov.code.label.mixin', 'mail.activity.mixin', 'his.mixin',
                'clinic.document.mixin']
    _inherits = {
        RES_PARNER: 'partner_id',
    }
    _rec_names_search = ['name', 'code', 'gov_code']

    def _rec_count(self):
        invoice = self.env['account.move']
        for rec in self:
            rec.invoice_count = invoice.sudo().search_count([('partner_id', '=', rec.partner_id.id)])

    partner_id = fields.Many2one(RES_PARNER, required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner', help='Partner-related data of the Patient')
    gov_code = fields.Char(string='Government Identity', copy=False, tracking=True)
    gov_code_label = fields.Char(compute="clinic_get_gov_code_label", string="Government Identity Label")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widow', 'Widow')], string='Marital Status', default="single")
    spouse_name = fields.Char("Spouse's Name")
    spouse_edu = fields.Char("Spouse's Education")
    spouse_business = fields.Char("Spouse's Business")
    education = fields.Char("Patient Education")
    is_corpo_tieup = fields.Boolean(string='Corporate Tie-Up',
                                    help="If not checked, these Corporate Tie-Up Group will not be visible at all.")
    corpo_company_id = fields.Many2one(RES_PARNER, string='Corporate Company',
                                       domain="[('is_company', '=', True),('customer_rank', '>', 0)]",
                                       ondelete='restrict')
    emp_code = fields.Char(string='Employee Code')
    user_id = fields.Many2one('res.users', string='Related User', ondelete='cascade',
                              help='User-related data of the patient')
    primary_physician_id = fields.Many2one('his.physician', 'Primary Care Doctor')
    clinic_tag_ids = fields.Many2many('his.patient.tag', 'patient_tag_his_rel', 'tag_id', 'patient_tag_id',
                                      string="HIS Tags")

    invoice_count = fields.Integer(compute='_rec_count', string='# Invoices')
    occupation = fields.Char("Occupation")
    clinic_religion_id = fields.Many2one('clinic.religion', string="Religion")
    caste = fields.Char("Tribe")
    nationality_id = fields.Many2one("res.country", string="Nationality")
    passport = fields.Char("Passport Number")
    active = fields.Boolean(string="Active", default=True)
    location_url = fields.Text(string="Location URL")
    age_to_birthday = fields.Integer(string="Age to Birthday")

    @api.onchange('age_to_birthday')
    def onchange_age_to_birthday(self):
        if self.age_to_birthday:
            if self.age_to_birthday >= 0 and self.age_to_birthday <= 200:
                today = fields.Date.today()
                birth_year = today.year - self.age_to_birthday
                self.birthday = today.replace(year=birth_year, month=1, day=1)
            else:
                raise UserError('Please enter a valid age between 0 and 200.')

    def clinic_get_gov_code_label(self):
        for rec in self:
            rec.gov_code_label = self.env.company.country_id.gov_code_label

    def check_gov_code(self, gov_code):
        patient = self.search([('gov_code', '=', gov_code)], limit=1)
        if patient and not self.env.context.get('clinic_avoid_gov_code_check', False):
            raise ValidationError(_('Patient already exists with Government Identity: %s.') % (gov_code))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code('his.patient') or ''
            company_id = vals.get('company_id')
            if company_id:
                company_id = self.env['res.company'].sudo().search([('id', '=', company_id)], limit=1)
            else:
                company_id = self.env.company
            if company_id.unique_gov_code and vals.get('gov_code'):
                self.check_gov_code(vals.get('gov_code'))
            vals['customer_rank'] = True
        return super().create(vals_list)

    def write(self, values):
        company_id = self.sudo().company_id or self.env.user.sudo().company_id
        if company_id.unique_gov_code and values.get('gov_code'):
            self.check_gov_code(values.get('gov_code'))
        return super(MatePatient, self).write(values)

    def view_invoices(self):
        invoices = self.env['account.move'].search(
            [('partner_id', '=', self.partner_id.id), ('move_type', 'in', ('out_invoice', 'out_refund'))])
        action = self.with_context(clinic_open_blank_list=True).clinic_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.partner_id.id,
            'default_patient_id': self.id,
        })
        return action

    @api.model
    def send_birthday_email(self):
        wish_template_id = self.env.ref('his_base.email_template_birthday_wish', raise_if_not_found=False)
        user_cmp_template = self.env.company.birthday_mail_template_id
        today = datetime.now()
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        patient_ids = self.search([('birthday', 'like', today_month_day)])
        for patient_id in patient_ids:
            if patient_id.email:
                wish_temp = patient_id.company_id.birthday_mail_template_id or user_cmp_template or wish_template_id
                wish_temp.sudo().send_mail(patient_id.id, force_send=True)

    def _compute_display_name(self):
        for rec in self:
            name = rec.name
            if rec.title and rec.title.shortcut:
                name = (rec.title.shortcut or '') + ' ' + (rec.name or '')
            rec.display_name = name

    @api.onchange('mobile')
    def _onchange_mobile_warning(self):
        if not self.mobile:
            return
        message = ''
        domain = [('mobile', '=', self.mobile)]
        if self._origin and self._origin.id:
            domain += [('id', '!=', self._origin.id)]
        patients = self.sudo().search(domain)
        for patient in patients:
            message += _('\nThe Mobile number is already registered with another Patient: %s, Government Identity:%s, DOB: %s.') % (patient.name, patient.gov_code, patient.birthday)
        if message:
            message += _('\n\n Are you sure you want to create a new Patient?')
            return {
                'warning': {
                    'title': _("Warning for Mobile Duplication"),
                    'message': message,
                }
            }

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        company = self.env.company
        if company.country_id.vat_label:
            for node in arch.xpath("//field[@name='gov_code']"):
                node.attrib["string"] = company.country_id.gov_code_label
        return arch, view

    @api.onchange('phone', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        if self.phone:
            self.phone = self._phone_format(fname='phone', force_format='INTERNATIONAL') or self.phone

    @api.onchange('mobile', 'country_id', 'company_id')
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self._phone_format(fname='mobile', force_format='INTERNATIONAL') or self.mobile

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
