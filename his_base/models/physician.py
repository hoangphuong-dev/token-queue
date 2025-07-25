# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
HIS_PHYSICIAN = 'his.physician'


class PhysicianSpecialty(models.Model):
    _name = 'physician.specialty'
    _description = "Physician Specialty"

    code = fields.Char(string='Code')
    name = fields.Char(string='Specialty', required=True, translate=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class PhysicianDegree(models.Model):
    _name = 'physician.degree'
    _description = "Physician Degree"

    name = fields.Char(string='Degree')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]


class Physician(models.Model):
    _name = HIS_PHYSICIAN
    _description = "Physician"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.users': 'user_id'}

    user_id = fields.Many2one('res.users', string='Related User', required=True,
                              ondelete='cascade', help='User-related data of the physician')
    code = fields.Char(string='Physician Code', default='New', tracking=True)
    degree_ids = fields.Many2many('physician.degree', 'physician_rel_education', 'physician_ids', 'degree_ids',
                                  string='Degree')
    specialty_id = fields.Many2one('physician.specialty', ondelete='set null', string='Specialty',
                                   help='Specialty Code', tracking=True)
    medical_license = fields.Char(string='Medical License', tracking=True)
    is_portal_user = fields.Boolean("Is Portal User")
    signature = fields.Binary('Signature')

    def clinic_make_dr_portal_user(self):
        group_portal = self.env.ref('base.group_portal')
        group_internal = self.env.ref('base.group_user')
        for rec in self:
            if rec.is_portal_user:
                rec.user_id.groups_id = [(6, 0, [group_portal.id])]
            else:
                rec.user_id.groups_id = [(6, 0, [group_internal.id])]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _("New")) == _("New"):
                vals['code'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code(
                    HIS_PHYSICIAN) or _("New")
            if vals.get('email'):
                vals['login'] = vals.get('email')
            # Mate: It creates issue in physician creation
            if vals.get('user_ids'):
                vals.pop('user_ids')

        res = super(Physician, self).create(vals_list)
        res.clinic_make_dr_portal_user()
        return res

    def write(self, values):
        res = super(Physician, self).write(values)
        if 'is_portal_user' in values:
            self.clinic_make_dr_portal_user()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
