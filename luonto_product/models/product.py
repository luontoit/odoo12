# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import pprint
import datetime
pp = pprint.PrettyPrinter(indent=4)

class ProductProduct(models.Model):
    _inherit = "product.product"

    is_exclude = fields.Boolean(string="Is Excluded Variant",
                                store=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def get_attr_no_buy(self):
        ids = self.attribute_line_ids.mapped('product_te9mplate_value_ids').filtered(
            lambda a: a.product_attribute_value_id.is_not_buy).ids
        return {'no_buys': ids}

    @api.multi
    def get_exclusions_recursive(self, attr_val, val_by_attr):
        print(val_by_attr)
        possible = []
        # get all possible exclusion values of current val's children
        for x in attr_val.attribute_value_ids.mapped('attribute_id').ids:
            possible += val_by_attr[x]

        # get all possible exclusion values not themselves children of the current val
        ex = {x for x in possible if x not in attr_val.attribute_value_ids.ids}
        # update the exclusion set

        child_ex = []
        # sub_ex = set()
        # for all attribute values in children attribute values
        for val in attr_val.attribute_value_ids:
            # if they themselves have children
            if val.attribute_value_ids:
                # recursively search for exclusions
                child_ex.append(self.get_exclusions_recursive(val, val_by_attr))
        if child_ex:
            ex.update(set.intersection(*child_ex))
            # exclusions.update(sub_ex)
        # sub_ex.update(ex)
        # TODO: check why updating and returning exclusions
        return ex

    # recursive algorithm
    # arg = attr_val, val_by_attr, exclusions

    # for each child attr,
    #

    # return all children's exclusions
    # aka node = blue > return {M, L, XL}
    # aka note = black > return {XS, XL}
    # want > {XL}

    @api.multi
    def get_exclusions(self, attribute_values, val_by_attr):
        #dictionary of sets
        all_ex = {}
        # For all attribute values with child attribute values
        for val in attribute_values.filtered(lambda v: v.attribute_value_ids):
            # Create dict with key = current attr val's id and value = set of exclusions
            # all_ex[val.id] = self.get_exclusions_recursive(val, val_by_attr, set())
            all_ex.setdefault(val.id, set()).update(self.get_exclusions_recursive(val, val_by_attr))
            # mirror the children
            for x in all_ex[val.id]:
                all_ex.setdefault(x, set()).add(val.id)
        return all_ex

    @api.multi
    def get_flat_exclusions(self):

        attr_vals = self.attribute_line_ids.mapped('value_ids')
        # Dict of key = attribute and value = attribute value
        # ex: {color.id: [red.id, blue.id, black.id]}
        val_by_attr = {}
        sub_attr = {}
        for main_attr_val in attr_vals:
            val_by_attr.setdefault(main_attr_val.attribute_id.id, []).append(main_attr_val.id)
            sub_attr[main_attr_val.id] = main_attr_val.attribute_value_ids.ids
        pp.pprint(val_by_attr)
        pp.pprint(sub_attr)

        flat_exclusions = self.get_exclusions(attr_vals, val_by_attr)
        pp.pprint(flat_exclusions)
        # for val in attr_vals:
        #     not_possible = sub_attr[val.id]
        #     flat_exclusions.setdefault(main_attr_val.id, []).append(main_attr_val.id)




class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        relation='sub_attr',
        column1='parent_attr',
        column2='child_attr',
        string="Sub Attribute Values",
        store=True)

    is_not_buy = fields.Boolean(string="Is Not Buyable",
                                help="Check this box to restrict customer from selecting and "
                                     "buying this product with this attribute.")

    def create_ex_attr_val(self, prod, main_attr, tmpl_attr):
        """Function that begins automatic attribute value addition to products based on sub attribute values

        Args:
            self: model self.
            prod: Current product gotten from the current attr_line.
            main_attr: Current main attribute value that is being iterated over.
            tmpl_attr: A dict of attributes+values for product.template.

        Returns:
            None

        """
        # EXAMPLE DIAGRAM

        # Attribute          Attribute Values
        # Product                  Couch
        #                         /      \
        # Fabric               cotton    poly
        #                       /  \    /    \
        # Color             blue    black     red


        # Use of product.template.attribute.value:
        # Materialized relationship between attribute values
        # and product template generated by the product.template.attribute.line

        # product.template.attribute.value on current product.template that
        # ARE attribute(fabric) and NOT current attribute(cotton) > should only be poly
        # ex: fabric:poly
        need_exclusion = self.env['product.template.attribute.value'].search([
            ['product_tmpl_id', '=', prod.id],
            ['attribute_id', '=', main_attr.attribute_id.id],
            ['product_attribute_value_id', '!=', main_attr.id]])
        # product.template.attribute.value on current product.template that
        # ARE of the same attribute(COLOR) as those in the sub attributes.
        # ex: color:blue, color:red, color:black
        possible_exclusion = self.env['product.template.attribute.value'].search([
            ['product_tmpl_id', '=', prod.id],
            ['attribute_id', 'in', list(tmpl_attr.keys())]])

        # product.template.attribute.values which need exclusion (fabric:poly)
        for need in need_exclusion:
            # product.template.attribute.values that might need to be excluded (color:blue, color:red, color:black)
            # filter:  possible(ex: color:red) not a sub attribute of the need's attribute value(fabric: poly)
            # filter2: filter out if possible is already an exclusion
            #TODO future: check case for parent1 > child1 > grandchild1
            # Do we need exclusions for parent1 and grandchild1
            for possible in possible_exclusion.filtered(lambda p: p.product_attribute_value_id not in need.product_attribute_value_id.attribute_value_ids and p not in need.exclude_for.value_ids):
                # if possible.product_attribute_value_id not in need.product_attribute_value_id.attribute_value_ids:
                has_tmpl_line = need.exclude_for.filtered(lambda x: x.product_tmpl_id == prod)
                if has_tmpl_line:
                    need.write({
                        'exclude_for': [(1, has_tmpl_line[0].id, {
                            'product_tmpl_id': prod.id,
                            'value_ids': [(4, possible.id, 0)]
                        })]
                    })
                # create exclusion line with current template
                else:
                    need.write({
                        'exclude_for': [(0, 0, {
                            'product_tmpl_id': prod.id,
                            'value_ids': [(4, possible.id, 0)]
                        })]
                    })
                # Handle reverse exclusion
                # ex: Poly not only exclude red but also red must exclude poly
                # This is for the UI purpose
                rev_has_tmpl_line = possible.exclude_for.filtered(lambda x: x.product_tmpl_id == prod)
                if rev_has_tmpl_line:
                    possible.write({
                        'exclude_for': [(1, rev_has_tmpl_line[0].id, {
                            'product_tmpl_id': prod.id,
                            'value_ids': [(4, need.id, 0)]
                        })]
                    })
                else:
                    possible.write({
                        'exclude_for': [(0, 0, {
                            'product_tmpl_id': prod.id,
                            'value_ids': [(4, need.id, 0)]
                        })]
                    })

    def line_attr_val_add(self, tmpl_attr, prod):
        """Function that begins automatic attribute value addition to products based on sub attribute values

        Args:
            self: model self.
            tmpl_attr: A dict of attributes+values for product.template.
            prod: Current product gotten from the current attr_line.

        Returns:
            None

        """
        # add sub attr val to attr lines IF the line for that attribute exists
        # for attr_id(ex: color) in attributes
        for attr_id in tmpl_attr.keys():
            # check if the line exists on the prod with the current attribute(ex: color)
            # exist = [v for v in prod.attribute_line_ids if attr_id == v.attribute_id.id]
            exist = prod.attribute_line_ids.filtered(lambda x: x.attribute_id.id == attr_id)
            if exist:
                # add the sub attr vals (ex: black, blue) to the existing attr line
                # av_attr = tmpl_attr[attr_id]
                av_attr = [x for x in tmpl_attr[attr_id] if x not in exist.value_ids.ids]
                for sub_id in av_attr:
                    exist[0].write({'value_ids': [(4, sub_id, 0)]})
            else:
                # otherwise create a new line with the attr_id(ex: color)
                val = [(4, s, 0) for s in tmpl_attr[attr_id]]
                # then add the sub attr vals (ex: black, blue)
                prod.write({
                    'attribute_line_ids': [(0, 0, {
                        'product_tmpl_id': prod.id,
                        'attribute_id': attr_id,
                        'value_ids': val,
                    })]
                })

    def prod_attr_val_add(self, main_attr, attr_lines, tmpl_attr):
        """Function that begins automatic attribute value addition to products based on sub attribute values

        Args:
            self: model self.
            main_attr: Current main attribute value that is being iterated over.
            attr_lines: All attribute lines with current attribute value(main_attr).
            tmpl_attr: A dict of attributes+values for product.template.

        Returns:
            None

        """
        # TODO Future?: make prefetch=false
        # TODO Future?: consider call search/search_read
        #
        # prefetching exclusion env for later
        combination_exclude = self.env['product.template.attribute.exclusion']
        # Add the sub attr val to the current attribute value(main_attr)
        # for line all attr lines on the a product template
        for line in attr_lines:
            # line will have unique prod.temp associated (ex: couch)
            prod = line.product_tmpl_id

            # add each of the sub attr val to the product
            self.line_attr_val_add(tmpl_attr, prod)

            # create the variants(prod.prod) for that prod.temp manually
            # using odoo function
            prod.create_variant_ids()

            # create the exclusions on the attribute values
            self.create_ex_attr_val(prod, main_attr, tmpl_attr)
            # Set exclusion boolean on the product variant if attribute values align
            for variant in prod.product_variant_ids:
                values_ids = variant.product_template_attribute_value_ids
                domain = [('product_template_attribute_value_id', 'in', values_ids.ids),
                          ('value_ids', 'in', values_ids.ids), ('product_tmpl_id', '=', prod.id)]
                is_ex = combination_exclude.search(domain)
                if is_ex:
                    variant.write({'is_exclude': True})

    def prepare_child_attr_val(self, attr_vals):
        # Loop through all the current attribute values in the recordset
        for attr in attr_vals:
            attr_vals = self.prepare_child_attr_val_recursive(attr, attr_vals)
        return attr_vals

    def prepare_child_attr_val_recursive(self, cur_attr, attr_vals):
        # Create a stop endpoint
        if cur_attr.attribute_value_ids:
            for attr in cur_attr.attribute_value_ids.filtered(lambda a: a not in attr_vals and a.attribute_value_ids):
                attr_vals |= attr
                return self.prepare_child_attr_val_recursive(attr, attr_vals)
        return attr_vals

    @api.model
    def create_attr_val_exclusions(self):
        """Function that begins automatic attribute value addition to products based on sub attribute values

        Args:
            self: model self.

        Returns:
            None

        """
        attr_vals = self.env['product.attribute.value'].search([('attribute_value_ids', '!=', False)])
        # Recursion only needed with past filter
        # attr_vals = self.prepare_child_attr_val(attr_vals)

        # for main_attr_val in attr_vals:
        #     tmpl_attr = {}
        #     # create a dict of attributes+values for product.template
        #     # ex: {color.id: [blue.id, black.id]}
        #     for sub_attr in main_attr_val.attribute_value_ids:
        #         tmpl_attr.setdefault(sub_attr.attribute_id.id, []).append(sub_attr.id)
        #
        #     # All attribute lines with current attribute value(main_attr)
        #     # lines are on product.template to generate product.template.attribute.value
        #     attr_lines = self.env['product.template.attribute.line'].search([['value_ids', 'in', main_attr_val.id]])
        #
        #     # Call function to do the value addition/exclusions
        #     if attr_lines:
        #         self.prod_attr_val_add(main_attr_val, attr_lines, tmpl_attr)

        # TODO: temp products var for looping
        products = self.env['product.template'].search([('id', '=', 3995)])

        for prod in products:
            flat_ex = {}
            attrs = prod.attribute_line_ids.mapped('value_ids')
            # pp.pprint(attrs)
            print(prod.name_get())
            print(attrs.name_get())
            # for a in attrs:
                #     print('placeholder')
                # flat_ex[a.id] =



    @api.model
    def create_attr_val_exclusions_server(self, records):
        """Function that begins automatic attribute value addition to products based on sub attribute values

        Args:
            self: model self.
            records: all the records

        Returns:
            None

        """
        # Grab all attribute values that has been modified in the last day and had sub att val
        attr_vals = records

        attr_vals = self.prepare_child_attr_val(attr_vals)

        for main_attr_val in attr_vals:
            tmpl_attr = {}
            # create a dict of attributes+values for product.template
            # ex: {color.id: [blue.id, black.id]}
            for sub_attr in main_attr_val.attribute_value_ids:
                tmpl_attr.setdefault(sub_attr.attribute_id.id, []).append(sub_attr.id)

            # All attribute lines with current attribute value(main_attr)
            # lines are on product.template to generate product.template.attribute.value
            attr_lines = self.env['product.template.attribute.line'].search([['value_ids', 'in', main_attr_val.id]])

            # Call function to do the value addition/exclusions
            if attr_lines:
                self.prod_attr_val_add(main_attr_val, attr_lines, tmpl_attr)
