from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

HIS_HEALTH_CHECK_PACKAGE = 'his.health.check.package'
HIS_HEALTH_CHECK_PACKAGE_GROUP_ORDER = 'his.health.check.package.group.order'
HIS_HEALTH_CHECK_GROUP = 'his.health.check.group'
HIS_HEALTH_CHECK_PACKAGE_LINE = 'his.health.check.package.line'


class CreateGroupSequenceWizard(models.TransientModel):
    _name = 'create.group.sequence.wizard'
    _description = 'Create Group Sequence Wizard'

    group_sequence_ids = fields.One2many(
        'create.group.sequence.line.wizard',
        'group_sequence_wizard_id',
        string='Group Sequences',
        help='The group sequences associated with this wizard.')

    package_id = fields.Many2one(
        HIS_HEALTH_CHECK_PACKAGE,
        string='Package',
        required=True)

    def create_group_sequence(self):
        self.env[HIS_HEALTH_CHECK_PACKAGE_GROUP_ORDER].create(
            [
                {
                    'package_id': line.package_id.id,
                    'sequence': line.sequence,
                    'group_id': line.group_id.id,
                } for line in self.group_sequence_ids
            ]
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': HIS_HEALTH_CHECK_PACKAGE_LINE,
            'name': _('Packages'),
            'views': [[False, "list"]],
            'view_id': self.env.ref('his_health_check.his_health_check_package_action').id,
            'target': 'main',
            'clear_breadcrumbs': True,
            'context': {
                'group_by': 'package_id',
            }
        }

    @api.model
    def action_save_group_sequence(self, *args, **kwargs):
        action = self.env.ref('his_health_check.action_mate_create_group_sequence_wizard').read()[0]
        action['context'] = {
            'dialog_size': 'extra-large',
        }
        action['target'] = 'current'
        action['view_mode'] = 'form'
        return action


class CreateGroupSequenceLineWizard(models.TransientModel):
    _name = 'create.group.sequence.line.wizard'
    _description = 'Create Group Sequence Line Wizard'

    group_sequence_wizard_id = fields.Many2one(
        'create.group.sequence.wizard',
        string='Group Sequence Wizard',
        help='The group sequence wizard associated with this line.')
    group_id = fields.Many2one(
        HIS_HEALTH_CHECK_GROUP,
        string='Group',
        help='The group associated with this line.')
    sequence = fields.Integer(
        string='Sequence',
        help='The sequence associated with this line.')
    package_id = fields.Many2one(
        HIS_HEALTH_CHECK_PACKAGE,
        string='Package',
        help='The package associated with this line.')
