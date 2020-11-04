# -*- coding: utf-8 -*-
import base64
import io
from collections import deque

from odoo import models, fields, api, _
from odoo.addons.pivot_scheduler.models.pivot_model import PivotModel
from odoo.tools import ustr
from odoo.tools.misc import xlwt

CRON_FIELDS = ['user_id', 'interval_number', 'interval_type', 'numbercall', 'doall', 'priority']


class AutoSendReport(models.Model):
    _name = 'auto_send_report.config'
    _description = 'Automatically send pivot'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    model_id = fields.Selection(selection='_list_all_models', string='Model', required=True)
    filter_id = fields.Many2one('ir.filters', string='User-defined Filter', required=True)
    recipient_ids = fields.Many2many('res.users', string='Recipients', required=True)
    active = fields.Boolean(default=True)
    # cron
    user_id = fields.Many2one('res.users', string='Scheduler User', default=lambda self: self.env.user, required=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], string='Interval Unit', default='months')
    numbercall = fields.Integer(string='Number of Calls', default=-1,
                                help='How many times the method is called,\na negative number indicates no limit.')
    doall = fields.Boolean(string='Repeat Missed', default=True,
                           help="Specify if missed occurrences should be executed when the server restarts.")
    priority = fields.Integer(default=5,
                              help='The priority of the job, as an integer: 0 means higher priority, 10 means lower priority.')
    cron_id = fields.Many2one('ir.cron', string='Related Cron', copy=False, delete='cascade')

    @api.model
    def _list_all_models(self):
        self._cr.execute("""select	distinct(m.model),
                                    m.name
                            from	ir_ui_view v
                            join	ir_model m on v.model = m.model
                            where	v.type='pivot'
                                    and v.active is true
                        """)
        return self._cr.fetchall()

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.filter_id = False

    @api.onchange('filter_id')
    def _onchange_filter_id(self):
        if self.filter_id and self.filter_id.user_id:
            self.recipient_ids = [(6, 0, [self.filter_id.user_id.id])]
        else:
            self.recipient_ids = False

    def _prepare_cron(self):
        self.ensure_one()
        return {
            "name": _("Pivot: %s") % self.name,
            "user_id": self.user_id.id,
            "model_id": self.env["ir.model"].search([("model", "=", self._name)], limit=1).id,
            "state": "code",
            "code": "model._run_cron(%s)" % self.ids,
            "interval_number": self.interval_number,
            "interval_type": self.interval_type,
            "numbercall": self.numbercall,
            "doall": self.doall,
            "priority": self.priority,
        }

    def action_send(self):
        email_template = self.env.ref('pivot_scheduler.pivot_auto_send_email_template')

        for config in self:
            data = config.filter_id.read(['model_id', 'domain', 'context', 'sort'])[0]
            for recipient in config.recipient_ids:
                export_data = PivotModel(data=data, env=config.env(user=recipient)).exportData()
                export_data['title'] = config.name + '_' + recipient.name + '_' + fields.Datetime.to_string(
                    fields.Datetime.context_timestamp(config.with_context(tz=recipient.tz), fields.Datetime.now()))
                export_data['recipient_name'] = recipient.name
                attachment_id = config.export_xls(export_data)
                email_values = {
                    'email_to': recipient.email,
                    'attachment_ids': [(6, 0, [attachment_id.id])],
                }
                email_template.with_context(lang=recipient.lang, partner_name=recipient.partner_id.name).send_mail(
                    config.id, force_send=True, email_values=email_values)

    @api.model
    def create(self, values):
        res = super(AutoSendReport, self).create(values)
        cron_id = self.env["ir.cron"].create(res._prepare_cron()).id
        res.write({'cron_id': cron_id})
        return res

    def write(self, values):
        cron_fields_to_update = list(set(CRON_FIELDS) & set(values.keys()))
        res = super(AutoSendReport, self).write(values)
        if cron_fields_to_update and self.cron_id:
            self.cron_id.write({field: values[field] for field in cron_fields_to_update})
        return res

    def toggle_active(self):
        self.cron_id.toggle_active()
        return super(AutoSendReport, self).toggle_active()

    def unlink(self):
        if self.cron_id:
            self.cron_id.unlink()
        return super(AutoSendReport, self).unlink()

    def _run_cron(self, config_ids):
        self.browse(config_ids).action_send()

    def export_xls(self, data):
        self.ensure_one()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(data['title'])
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
        bold = xlwt.easyxf("font: bold on;")

        measure_count = data['measure_count']
        origin_count = data['origin_count']

        # Step 1: writing col group headers
        col_group_headers = data['col_group_headers']

        # x,y: current coordinates
        # carry: queue containing cell information when a cell has a >= 2 height
        #      and the drawing code needs to add empty cells below
        x, y, carry = 1, 0, deque()
        for i, header_row in enumerate(col_group_headers):
            worksheet.write(i, 0, '', header_plain)
            for header in header_row:
                while (carry and carry[0]['x'] == x):
                    cell = carry.popleft()
                    for j in range(measure_count * (2 * origin_count - 1)):
                        worksheet.write(y, x + j, '', header_plain)
                    if cell['height'] > 1:
                        carry.append({'x': x, 'height': cell['height'] - 1})
                    x = x + measure_count * (2 * origin_count - 1)
                for j in range(header['width']):
                    worksheet.write(y, x + j, header['title'] if j == 0 else '', header_plain)
                if header['height'] > 1:
                    carry.append({'x': x, 'height': header['height'] - 1})
                x = x + header['width']
            while (carry and carry[0]['x'] == x):
                cell = carry.popleft()
                for j in range(measure_count * (2 * origin_count - 1)):
                    worksheet.write(y, x + j, '', header_plain)
                if cell['height'] > 1:
                    carry.append({'x': x, 'height': cell['height'] - 1})
                x = x + measure_count * (2 * origin_count - 1)
            x, y = 1, y + 1

        # Step 2: writing measure headers
        measure_headers = data['measure_headers']

        if measure_headers:
            worksheet.write(y, 0, '', header_plain)
            for measure in measure_headers:
                style = header_bold if measure['is_bold'] else header_plain
                worksheet.write(y, x, measure['title'], style)
                for i in range(1, 2 * origin_count - 1):
                    worksheet.write(y, x + i, '', header_plain)
                x = x + (2 * origin_count - 1)
            x, y = 1, y + 1

        # Step 3: writing origin headers
        origin_headers = data['origin_headers']

        if origin_headers:
            worksheet.write(y, 0, '', header_plain)
            for origin in origin_headers:
                style = header_bold if origin['is_bold'] else header_plain
                worksheet.write(y, x, origin['title'], style)
                x = x + 1
            y = y + 1

        # Step 4: writing data
        x = 0
        for row in data['rows']:
            worksheet.write(y, x, row['indent'] * '     ' + ustr(row['title']), header_plain)
            for cell in row['values']:
                x = x + 1
                if cell.get('is_bold', False):
                    worksheet.write(y, x, cell['value'], bold)
                else:
                    worksheet.write(y, x, cell['value'])
            x, y = 0, y + 1
        f = io.BytesIO()
        workbook.save(f)
        f.seek(0)
        filename = data['title'] + '.xls'
        return self.env.get('ir.attachment').create({
            'name': filename,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'datas': base64.b64encode(f.read()),
            'mimetype': 'application/vnd.ms-excel',
        })


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        pivot_filter_id = self.env.context.get('pivot_filter_id')
        if pivot_filter_id:
            pivot_filter = self.env['ir.filters'].browse(pivot_filter_id)
            if pivot_filter and pivot_filter.user_id:
                domain = [('id', '=', pivot_filter.user_id.id)]
            else:
                model = self.env['ir.model'].search([('model', '=', pivot_filter.model_id)], limit=1)
                user_ids = model.mapped('access_ids').filtered(lambda a: a.perm_read).mapped('group_id.users').filtered(
                    lambda x: x.email).ids
                domain = [('id', 'in', user_ids)]
        args += domain
        return super(Users, self).name_search(name=name, args=args, operator=operator, limit=limit)
