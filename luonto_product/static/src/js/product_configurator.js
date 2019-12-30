odoo.define('luonto_product.ProductConfiguratorFormRendererLuonto', function (require) {
'use strict';

var ProductConfiguratorFormRenderer = require('sale.ProductConfiguratorFormRenderer');
var OptionalProductsModal = require('sale.OptionalProductsModal');
var ProductConfiguratorFormController = require('sale.ProductConfiguratorFormController');
var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');



console.log("DO we get here??"); // This gets triggered

var ProductConfiguratorFormRendererLuonto = ProductConfiguratorFormRenderer.include({
    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        console.log("Are we inside start??"); // Not triggered

        var $temp = this.$el.find('input[name="add_qty"]');

        $temp.addClass("testing-here");

        console.log($temp);
    },
//        /**
//     * @override
//     */
//    _onChangeCombination:function (ev, $parent, combination) {
//        this._super.apply(this, arguments);
//        console.log("Are we inside onchange combination??"); // Not triggered
//    },

    _onFieldChanged: function (event) {
        this._super.apply(this, arguments);

        console.log("inside onfield change");
    },

    triggerVariantChange: function ($container) {
        this._super.apply(this, arguments);
        console.log("HELLO var change??");
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

            var values = [];
            var product_exclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').exclusions
            console.log("THESE ARE THE PROD EXCLUSIONS: ")
            console.log(product_exclusions)

            var no_buy_variants = $parent.find('ul[data-no_buy]').data('no_buy').no_buys
            console.log("These are the no_buy var:")
            console.log(no_buy_variants)

            // Grab the values that are currently selected
            var values = [];
            console.log("NEXT LOG: ")
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                values.push(+$(el).val());
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
                var to_hide = product_exclusions[val]
                // Hide all related attribute values
                for (var h of to_hide) {
                    $('input[value="'+ h +'"]').remove();
                    $('option[value="'+ h +'"]').remove();
                }
            }

            var findNoBuy = no_buy_variants.some(r=> values.indexOf(r) >= 0)

            console.log("IF no buy selected: ")
            console.log(findNoBuy)

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
