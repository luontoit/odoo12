odoo.define('website_sale.new_cart', function (require) {
"use strict";
    $("form.form-inline").addClass("pull-left");
    var cart = require('website_sale.cart');
    var web_editor_base = require('web_editor.base');
    var ajax = require("web.ajax")
    var core = require("web.core")

    web_editor_base.ready().then(function(){
        function hide_excluded_products(source_form, event) {
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

            var $form = source_form;
            var values = [];
            var attr_values = [];

            var $parent = $(event.target).closest('.js_product');
            var product_exclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').exclusions
            var no_buy_variants = $parent.find('ul[data-no_buy]').data('no_buy').no_buys
            var flat_ex = $parent.find('ul[data-flat_ex]').data('flat_ex')

            // Grab the values that are currently selected
            var values = [];
            var $productSelects = []
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                values.push(+$(el).val());
//                $('[value=' + +$(el).val() + ']', el)
//                var option_sel = $(el).find('option:selected').data('value_id');
                attr_values.push($(el).find('option:selected').data('value_id'));
                $(el).each(function(){
                    setOriginalSelect($(this));
                    restoreOptions($(this), +$(el).val());
                });
            });

//            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
//                attr_values.push(+$(el).getAttribute('data-value_id'));
////                $(el).each(function(){
////                    setOriginalSelect($(this))
////                    restoreOptions($(this), +$(el).val());
////
////                });
//            });

            for (var val of values) {
                if (no_buy_variants.includes(val)){
                    $('input[value="'+ val +'"]').addClass('no_buy_grey');
                    $('option[value="'+ val +'"]').addClass('no_buy_grey');
                };
//                var to_hide = product_exclusions[val]
                // Hide all related attribute values
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

        $('input[type="radio"].js_variant_change, select.js_variant_change').on('change', function(event) {
            var $form = $(this).closest('form');
            hide_excluded_products($form, $(this).val(), event);
        });

        // Trigger the change everytime Product page is loaded
        $( document ).ready(function() {
            $('input[type="radio"].js_variant_change, select.js_variant_change').trigger('change');
        });

    });

});