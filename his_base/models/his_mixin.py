# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import base64
from io import BytesIO

IR_ACTIONS = "ir.actions.actions"
IR_MODULE_MODULE = 'ir.module.module'


class MateQrcodeMixin(models.AbstractModel):
    _name = "clinic.qrcode.mixin"
    _description = "QrCode Mixin"

    unique_code = fields.Char("Unique UID")
    qr_image = fields.Binary("QR Code", compute='clinic_generate_qrcode')

    def clinic_generate_qrcode(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            import qrcode
            model_name = (rec._name).replace('.', '')
            url = base_url + '/validate/%s/%s' % (model_name, rec.unique_code)
            data = BytesIO()
            qrcode.make(url.encode(), box_size=4).save(data, optimise=True, format='PNG')
            qrcode = base64.b64encode(data.getvalue()).decode()
            rec.qr_image = qrcode


class MateHisMixin(models.AbstractModel):
    _name = "his.mixin"
    _description = "HIS Mixin"

    def clinic_prepare_invoice_data(self, partner, patient, product_data, inv_data):
        fiscal_position_id = self.env['account.fiscal.position']._get_fiscal_position(partner)
        data = {
            'partner_id': partner.id,
            'patient_id': patient and patient.id,
            'move_type': inv_data.get('move_type', 'out_invoice'),
            'ref': self.name,
            'invoice_origin': self.name,
            'currency_id': self.env.company.currency_id.id,
            'invoice_line_ids': self.clinic_get_invoice_lines(product_data, partner, inv_data, fiscal_position_id),
            'physician_id': inv_data.get('physician_id', False),
            'hospital_invoice_type': inv_data.get('hospital_invoice_type', False),
            'fiscal_position_id': fiscal_position_id and fiscal_position_id.id or False,
        }
        if inv_data.get('ref_physician_id', False):
            data['ref_physician_id'] = inv_data.get('ref_physician_id', False)
        if inv_data.get('appointment_id', False):
            data['appointment_id'] = inv_data.get('appointment_id', False)

        module = self.env[IR_MODULE_MODULE].sudo()
        if module.search(
                [('name', '=', 'his_doctor_fee_reimbursement'), ('state', '=', 'installed')]) and self.env.context.get(
                'commission_partner_ids', False):
            data['commission_partner_ids'] = [(6, 0, [self.env.context.get('commission_partner_ids')])]
        return data

    @api.model
    def clinic_create_invoice(self, partner, patient=False, product_data=None, inv_data=None):
        if product_data is None:
            product_data = []
        if inv_data is None:
            inv_data = {}
        inv_data = self.clinic_prepare_invoice_data(partner, patient, product_data, inv_data)
        invoice = self.env['account.move'].create(inv_data)
        invoice._onchange_partner_id()
        for line in invoice.invoice_line_ids:
            line._get_computed_taxes()
        return invoice

    def _get_tax_ids_for_product(self, product, company_id, move_type, fiscal_position_id):
        """Helper method to get tax IDs for a product"""
        if move_type in ['out_invoice', 'out_refund']:
            tax_ids = product.taxes_id.filtered(lambda t: t.company_id.id == company_id)
        else:
            tax_ids = product.supplier_taxes_id.filtered(lambda t: t.company_id == company_id)

        if tax_ids and fiscal_position_id:
            tax_ids = fiscal_position_id.map_tax(tax_ids._origin)

        return [(6, 0, tax_ids.ids)] if tax_ids else None

    def _create_product_line_data(self, data, product, partner, inv_data, fiscal_position_id):
        """Helper method to create product line data"""
        quantity = data.get('quantity', 1.0)
        uom_id = data.get('product_uom_id')
        discount = data.get('discount', 0.0)
        company_id = self.env.context.get('default_company_id') or self.env.company.id

        clinic_pricelist_id = self.env.context.get('clinic_pricelist_id')

        if 'price_unit' in data:
            price = data.get('price_unit')
        else:
            price = product.with_context(clinic_pricelist_id=clinic_pricelist_id)._clinic_get_partner_price(
                quantity, uom_id, partner)

        tax_ids = self._get_tax_ids_for_product(product, company_id, inv_data.get('move_type', 'out_invoice'),
                                                fiscal_position_id)

        return {
            'name': data.get('name', product.get_product_multiline_description_sale()),
            'product_id': product.id,
            'price_unit': price,
            'quantity': quantity,
            'discount': discount,
            'product_uom_id': uom_id or product.uom_id.id or False,
            'tax_ids': tax_ids,
            'display_type': 'product',
        }

    def _create_non_product_line_data(self, data):
        """Helper method to create non-product line data"""
        return {
            'name': data.get('name'),
            'display_type': data.get('display_type', 'line_section'),
        }

    @api.model
    def clinic_get_invoice_lines(self, product_data, partner, inv_data, fiscal_position_id):
        lines = []
        for data in product_data:
            product = data.get('product_id')

            if product and product.id:
                line_data = self._create_product_line_data(data, product, partner, inv_data, fiscal_position_id)
            else:
                line_data = self._create_non_product_line_data(data)

            lines.append((0, 0, line_data))

        return lines

    def _get_product_price(self, product_data, product, invoice):
        """Helper method to get product price"""
        quantity = product_data.get('quantity', 1.0)
        uom_id = product_data.get('product_uom_id')
        clinic_pricelist_id = self.env.context.get('clinic_pricelist_id')

        if product_data.get('price_unit'):
            return product_data.get('price_unit', product.list_price)
        else:
            return product.with_context(clinic_pricelist_id=clinic_pricelist_id)._clinic_get_partner_price(
                quantity, uom_id, invoice.partner_id)

    def _create_product_move_line_data(self, product_data, product, invoice, price, tax_ids, account_id):
        """Helper method to create product move line data"""
        quantity = product_data.get('quantity', 1.0)
        uom_id = product_data.get('product_uom_id')
        discount = product_data.get('discount', 0.0)

        return {
            'move_id': invoice.id,
            'name': product_data.get('name', product.get_product_multiline_description_sale()),
            'product_id': product.id,
            'account_id': account_id.id,
            'price_unit': price,
            'quantity': quantity,
            'discount': discount,
            'product_uom_id': uom_id,
            'tax_ids': tax_ids,
            'display_type': 'product',
        }

    def _add_commission_data(self, data, clinic_commission_partner_ids):
        """Helper method to add commission data if module is installed"""
        module = self.env[IR_MODULE_MODULE].sudo()
        if (module.search([('name', '=', 'clinic_doctor_fee_reimbursement'), ('state', '=', 'installed')])
                and clinic_commission_partner_ids):
            data['clinic_commission_partner_ids'] = [(6, 0, clinic_commission_partner_ids)]
        return data

    @api.model
    def clinic_create_invoice_line(self, product_data, invoice):
        product = product_data.get('product_id')
        move_line = self.env['account.move.line']
        clinic_commission_partner_ids = product_data.get('clinic_commission_partner_ids', [])

        if product:
            price = self._get_product_price(product_data, product, invoice)
            tax_ids = self._get_tax_ids_for_product(product, invoice.company_id.id, invoice.move_type,
                                                    invoice.fiscal_position_id)
            account_id = product.property_account_income_id or product.categ_id.property_account_income_categ_id

            data = self._create_product_move_line_data(product_data, product, invoice, price, tax_ids, account_id)
            data = self._add_commission_data(data, clinic_commission_partner_ids)

            line = move_line.with_context(check_move_validity=False).create(data)
        else:
            line = move_line.with_context(check_move_validity=False).create({
                'move_id': invoice.id,
                'name': product_data.get('name'),
                'display_type': 'line_section',
            })

        return line

    def clinic_action_view_invoice(self, invoices):
        action = self.env[IR_ACTIONS]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.id
        elif self.env.context.get('clinic_open_blank_list'):
            # Allow to open invoices
            action['domain'] = [('id', 'in', invoices.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        action['context'] = context
        return action

    @api.model
    def assign_given_lots(self, move, lot_id, lot_qty):
        move_line = self.env['stock.move.line'].sudo()
        move_line_id = move_line.search([('move_id', '=', move.id), ('lot_id', '=', False)], limit=1)
        if move_line_id:
            move_line_id.lot_id = lot_id

    def consume_material(self, source_location_id, dest_location_id, product_data):
        product = product_data['product']
        move = self.env['stock.move'].sudo().create({
            'name': self.name or product.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': product_data.get('qty', 1.0),
            'date': product_data.get('date', fields.datetime.now()),
            'location_id': source_location_id,
            'location_dest_id': dest_location_id,
            'state': 'draft',
            'origin': self.name,
            'quantity': product_data.get('qty', 1.0),
            'picked': True,
        })
        move._action_confirm()
        move._action_assign()
        if product_data.get('lot_id', False):
            lot_id = product_data.get('lot_id')
            lot_qty = product_data.get('qty', 1.0)
            self.sudo().assign_given_lots(move, lot_id, lot_qty)
        if move.state == 'assigned':
            move._action_done()
        return move

    def clinic_apply_invoice_exemption(self):
        for rec in self:
            rec.invoice_exempt = False if rec.invoice_exempt else True

    def _process_kit_product(self, line, source_location_id, dest_location_id, field_to_update, rec):
        """Helper method to process kit products"""
        move_ids = []
        for kit_line in line.product_id.clinic_kit_line_ids:
            if kit_line.product_id.tracking != 'none':
                raise UserError(
                    "In Consumable lines Kit product with component having lot/serial tracking is not allowed. Please remove such kit product from consumable lines.")
            move = self.consume_material(source_location_id, dest_location_id,
                                         {'product': kit_line.product_id,
                                          'qty': kit_line.product_qty * line.qty})
            if field_to_update:
                move[field_to_update] = rec.id
            move_ids.append(move.id)

        # Set move_id on line also to avoid issue
        line.move_id = move.id
        line.move_ids = [(6, 0, move_ids)]
        return move

    def _process_regular_product(self, line, source_location_id, dest_location_id, field_to_update, rec):
        """Helper method to process regular products"""
        move = self.consume_material(source_location_id, dest_location_id,
                                     {'product': line.product_id, 'qty': line.qty,
                                      'lot_id': line.lot_id and line.lot_id.id or False, })
        line.move_id = move.id
        if field_to_update:
            move[field_to_update] = rec.id
        return move

    def _should_process_line(self, line):
        """Helper method to check if line should be processed"""
        return (line.display_type == 'product' and not line.move_id and not line.ignore_stock_move)

    def clinic_consume_material(self, field_to_update=False):
        his_installed = self.env[IR_MODULE_MODULE].sudo().search([('name', '=', 'his'), ('state', '=', 'installed')])
        for rec in self:
            source_location_id, dest_location_id = rec.clinic_get_consume_locations()
            for line in rec.consumable_line_ids.filtered(self._should_process_line):
                if (his_installed and line.product_id.is_kit_product and line.product_id.clinic_kit_line_ids):
                    self._process_kit_product(line, source_location_id, dest_location_id, field_to_update, rec)
                else:
                    self._process_regular_product(line, source_location_id, dest_location_id, field_to_update, rec)

    # CHECK and if needed put in separate mixin
    def get_clinic_kit_lines(self):
        if not self.clinic_kit_id:
            raise UserError("Please Select Kit first.")

        lines = []
        for line in self.clinic_kit_id.clinic_kit_line_ids:
            lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'qty': line.product_qty * self.clinic_kit_qty,
            }))
        self.consumable_line_ids = lines

    @api.model
    def clinic_get_department_domain(self):
        return [
            ('patient_department', '=', True),
            ('id', 'in', self.env.user.department_ids.ids)
        ]


class CalendarMixin(models.AbstractModel):
    _name = "clinic.calendar.mixin"
    _description = "Calendar Mixin"

    clinic_calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event')

    # Hook method to update in related model
    def clinic_prepare_calendar_data(self):
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)])
        data = {
            'name': _("%s: %s") % (model_id.name, self.name),
            'clinic_medical_event': True,
            'res_id': self.id,
            'res_model_id': model_id.id
        }
        return data

    def _should_skip_calendar_creation(self, rec):
        """Helper method to check if calendar creation should be skipped"""
        return (hasattr(rec, 'state') and rec.state in ['draft'])

    def _should_delete_calendar_event(self, rec):
        """Helper method to check if calendar event should be deleted"""
        return (hasattr(rec, 'state') and rec.state in ['cancel'])

    def _get_calendar_context(self):
        """Helper method to get calendar context"""
        return {
            'clinic_avoid_check': True,
            'no_mail_to_attendees': True,
            'dont_notify': True
        }

    def _update_existing_calendar_event(self, rec, calendar_data):
        """Helper method to update existing calendar event"""
        context = self._get_calendar_context()
        rec.clinic_calendar_event_id.with_context(**context).write(calendar_data)

    def _create_new_calendar_event(self, rec, calendar_data):
        """Helper method to create new calendar event"""
        context = self._get_calendar_context()
        calendar_event = self.env['calendar.event']
        clinic_calendar_event_id = calendar_event.with_context(**context).create(calendar_data)
        rec.clinic_calendar_event_id = clinic_calendar_event_id.id

    def _delete_calendar_event(self, rec):
        """Helper method to delete calendar event"""
        context = self._get_calendar_context()
        rec.clinic_calendar_event_id.with_context(**context).unlink()

    def clinic_calendar_event(self, user_field=False):
        """Process calendar events for records with reduced cognitive complexity"""
        for rec in self:
            if not rec[user_field]:
                self._handle_no_user_field(rec)
                continue

            self._handle_user_field_present(rec)

    def _handle_no_user_field(self, rec):
        """Handle case when user_field is not present"""
        if rec.clinic_calendar_event_id:
            self._delete_calendar_event(rec)

    def _handle_user_field_present(self, rec):
        """Handle case when user_field is present"""
        calendar_data = rec.clinic_prepare_calendar_data()

        if not self._has_valid_calendar_data(calendar_data):
            return

        if self._should_skip_calendar_creation(rec):
            return

        self._process_calendar_event(rec, calendar_data)

        if self._should_delete_calendar_event(rec):
            self._delete_calendar_event(rec)

    def _has_valid_calendar_data(self, calendar_data):
        """Check if calendar data has valid start and stop times"""
        return calendar_data.get('start') and calendar_data.get('stop')

    def _process_calendar_event(self, rec, calendar_data):
        """Process calendar event creation or update"""
        if rec.clinic_calendar_event_id:
            self._update_existing_calendar_event(rec, calendar_data)
        else:
            self._create_new_calendar_event(rec, calendar_data)


class MateDocumentMixin(models.AbstractModel):
    _name = "clinic.document.mixin"
    _description = "Document Mixin"

    def _clinic_get_attachments(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id)])
        return attachments

    def _clinic_attachment_count(self):
        for rec in self:
            attachments = rec._clinic_get_attachments()
            rec.attach_count = len(attachments)
            rec.attachment_ids = [(6, 0, attachments.ids)]

    attach_count = fields.Integer(compute="_clinic_attachment_count", readonly=True, string="Documents")
    attachment_ids = fields.Many2many('ir.attachment', 'attachment_his_rel', 'record_id', 'attachment_id',
                                      compute="_clinic_attachment_count", string="Attachments")

    def action_view_attachments(self):
        self.ensure_one()
        action = self.env[IR_ACTIONS]._for_xml_id("base.action_attachment")
        action['domain'] = [('id', 'in', self.attachment_ids.ids)]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.id,
            'default_is_document': True}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
