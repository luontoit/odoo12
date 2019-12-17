# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_exclude = fields.Boolean(string="Is Excluded Variant",
                                store=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def get_attr_no_buy(self):
        return self.attribute_line_ids.mapped('product_template_value_ids').filtered(lambda a: a.product_attribute_value_id.is_not_buy).ids


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='sub_attr',
        column1='parent_attr',
        column2='child_attr',
        string="Sub Attribute Values")

    is_not_buy = fields.Boolean(string="Is Not Buyable",
                               help="Check this box to restrict customer from selecting and "
                                    "buying this product with this attribute.")

    @api.multi
    def write(self, values):
        res = super(ProductAttributeValue, self).write(values)

        print("WE GOT TO WRITE HERE")
        # # All attribute value selected(ex:cotton)
        # for r in self.filtered(lambda r: r.attribute_value_ids):
        #     tmpl_attr = {}
        #     # create a dict of attributes+values for product.template
        #     for sub in r.attribute_value_ids:
        #         tmpl_attr.setdefault(sub.attribute_id.id, []).append(sub.id)
        #
        #     # All attribute lines with current attribute value(r)
        #     attr_lines = self.env['product.template.attribute.line'].search([['value_ids', 'in', r.id]])
        #     # prefetching exclusion env
        #     combination_exclude = self.env['product.template.attribute.exclusion']
        #
        #     # Add the sub attr val to the current attribute value(r)
        #     for line in attr_lines:
        #         prod = line.product_tmpl_id
        #         for key in tmpl_attr.keys():
        #             exist = [v for v in prod.attribute_line_ids if key == v.attribute_id.id]
        #             if exist:
        #                 for sub_id in tmpl_attr[key]:
        #                     exist[0].write({'value_ids': [(4, sub_id, 0)]})
        #             else:
        #                 val = [(4, s, 0) for s in tmpl_attr[key]]
        #                 prod.write({
        #                     'attribute_line_ids': [(0, 0, {
        #                         'product_tmpl_id': prod.id,
        #                         'attribute_id': key,
        #                         'value_ids': val,
        #                     })]
        #                 })
        #         prod.create_variant_ids()
        #
        #         # product.template.attribute.value on current product.template that ARE attribute(fabric) and NOT current attribute(poly) > should only be cotton
        #         need_exclusion = self.env['product.template.attribute.value'].search([
        #             ['product_tmpl_id', '=', prod.id],
        #             ['attribute_id', '=', r.attribute_id.id],
        #             ['product_attribute_value_id', '!=', r.id]])
        #         # product.template.attribute.value on current product.template that are of the same attribute as those in the sub attributes.
        #         possible_exclusion = self.env['product.template.attribute.value'].search([
        #             ['product_tmpl_id', '=', prod.id],
        #             ['attribute_id', 'in', list(tmpl_attr.keys())]])
        #
        #         # product.template.attribute.values which need exclusion
        #         for need in need_exclusion:
        #             # product.template.attribute.values that might need to be excluded
        #             for ex in possible_exclusion:
        #                 # if not sub attributes of the need
        #                 if ex.product_attribute_value_id not in need.product_attribute_value_id.attribute_value_ids:
        #                     has_tmpl_line = [t for t in need.exclude_for if
        #                                      t.product_tmpl_id == need.product_tmpl_id]
        #                     if has_tmpl_line:
        #                         need.write({
        #                             'exclude_for': [(1, has_tmpl_line[0].id, {
        #                                 'product_tmpl_id': need.product_tmpl_id.id,
        #                                 'value_ids': [(4, ex.id, 0)]
        #                             })]
        #                         })
        #                     # create exclusion line with current template
        #                     else:
        #                         need.write({
        #                             'exclude_for': [(0, 0, {
        #                                 'product_tmpl_id': need.product_tmpl_id.id,
        #                                 'value_ids': [(4, ex.id, 0)]
        #                             })]
        #                         })
        #                     # Handle reverse exclusion
        #                     rev_has_tmpl_line = [t for t in ex.exclude_for if
        #                                          t.product_tmpl_id == ex.product_tmpl_id]
        #                     if rev_has_tmpl_line:
        #                         ex.write({
        #                             'exclude_for': [(1, rev_has_tmpl_line[0].id, {
        #                                 'product_tmpl_id': ex.product_tmpl_id.id,
        #                                 'value_ids': [(4, need.id, 0)]
        #                             })]
        #                         })
        #                     else:
        #                         ex.write({
        #                             'exclude_for': [(0, 0, {
        #                                 'product_tmpl_id': ex.product_tmpl_id.id,
        #                                 'value_ids': [(4, need.id, 0)]
        #                             })]
        #                         })
        #         # Set exclusion boolean on the product variant if attribute values align
        #         cur_var = prod.product_variant_ids
        #         for var in cur_var:
        #             values_ids = var.product_template_attribute_value_ids
        #             domain = [('product_template_attribute_value_id', 'in', values_ids.ids),
        #                       ('value_ids', 'in', values_ids.ids), ('product_tmpl_id', '=', prod.id)]
        #             is_ex = combination_exclude.search(domain)
        #             if is_ex:
        #                 var.write({'is_exclude': True})
        # return res
