odoo.define('luonto_product.ProductConfiguratorFormRendererLuonto', function (require) {
'use strict';

var ProductConfiguratorFormRenderer = require('sale.ProductConfiguratorFormRenderer');
var OptionalProductsModal = require('sale.OptionalProductsModal');
var ProductConfiguratorFormController = require('sale.ProductConfiguratorFormController');
var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');

var ProductConfiguratorFormRendererLuonto = ProductConfiguratorFormRenderer.include({
    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        var $temp = this.$el.find('input[name="add_qty"]');
    },

    _onFieldChanged: function (event) {
        this._super.apply(this, arguments);
    },

    triggerVariantChange: function ($container) {
        this._super.apply(this, arguments);
    },

    _checkExclusions: function ($parent, combination) {
        this._super.apply(this, arguments);
        function hide_excluded_products($parent) {
            function setOriginalSelect ($select) {
                if ($select.data("originalHTML") == undefined) {
                    $select.find('option').each( function() {
                        $(this).removeAttr('class');
                        $(this).removeAttr('selected');
                    }
                    );
                    $select.data("originalHTML", $select.html());
                } // If it's already there, don't re-set it
            }

            function removeOptions ($select, $options) {
                setOriginalSelect($select);
                $options.remove();
            }

            function restoreOptions ($select, cur_selected) {
                var ogHTML = $select.data("originalHTML");
                if (ogHTML != undefined) {
                    $select.html(ogHTML);
                }
                $select.find('option').each( function() {
                        if ($(this).val() == cur_selected) {
                            $(this).attr("selected","selected");
                        }
                    });
            }

            var product_exclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').exclusions
            var no_buy_variants = $parent.find('ul[data-no_buy]').data('no_buy').no_buys
            var flat_ex = $parent.find('ul[data-flat_ex]').data('flat_ex')

            // Grab the values that are currently selected
            var values = [];
            var attr_values = [];
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                values.push(+$(el).val());
                attr_values.push($(el).find('option:selected').data('value_id'));
                $(el).each(function(){
                    setOriginalSelect($(this));
                    restoreOptions($(this), +$(el).val());
                });
            });

            for (var val of values) {
                if (no_buy_variants.includes(val)){
                    $('input[value="'+ val +'"]').addClass('no_buy_grey');
                    $('option[value="'+ val +'"]').addClass('no_buy_grey');
                };
//                var to_hide = product_exclusions[val]
//                // Hide all related attribute values
//                for (var h of to_hide) {
//                    $('input[value="'+ h +'"]').remove();
//                    $('option[value="'+ h +'"]').remove();
//                }
            }

            for (var attr of attr_values) {
                var hide = flat_ex[attr]
                for (var h of hide) {
                    $('input[data-value_id="'+ h +'"]').remove();
                    $('option[data-value_id="'+ h +'"]').remove();
                }
            }

            var findNoBuy = no_buy_variants.some(r=> values.indexOf(r) >= 0)
            $parent.find('#add_to_cart').removeClass('stop_buy')

            if (findNoBuy) {
                    $parent.find('#add_to_cart').addClass('stop_buy')
                };
        } // End hide_excluded_products
        hide_excluded_products($parent)
    },
});

return ProductConfiguratorFormRendererLuonto;

});
