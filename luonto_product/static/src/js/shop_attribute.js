odoo.define('website_sale.new_cart', function (require) {
"use strict";
    $("form.form-inline").addClass("pull-left");
    var cart = require('website_sale.cart');
    var web_editor_base = require('web_editor.base');
    var ajax = require("web.ajax")
    var core = require("web.core")

    web_editor_base.ready().then(function(){

        function hide_excluded_products(event) {

            function setOriginalSelect ($select) {
                if ($select.data("originalHTML") == undefined) {
                    $select.find('option').each( function() {
                        $(this).removeAttr('class');
                        $(this).removeAttr('selected');
                    });
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
            var attr_values = [];

            var $parent = $(event.target).closest('.js_product');
            var no_buy_variants = $parent.find('ul[data-no_buy]').data('no_buy').no_buys;
            var flat_ex = $parent.find('ul[data-flat_ex]').data('flat_ex');

            // Grab the values that are currently selected
            var $productSelects = [];
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];

            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                values.push(+$(el).val());
                attr_values.push($(el).find('option:selected').data('attr_val_id'));
                $(el).each(function(){
                    setOriginalSelect($(this));
                    restoreOptions($(this), +$(el).val());
                });
            });

            for (var attr of attr_values) {
                var hide = flat_ex[attr];
                for (var h of hide) {
                    $('input[data-attr_val_id="'+ h +'"]').remove();
                    $('option[data-attr_val_id="'+ h +'"]').remove();
                }
            }

            var findNoBuy = no_buy_variants.some(r=> values.indexOf(r) >= 0);
            $parent.find('#add_to_cart').removeClass('stop_buy');
            if (findNoBuy) {
                $parent.find('#add_to_cart').addClass('stop_buy');
            };
        }; // End hide_excluded_products

        function auto_select(event) {
            var $parent = $(event.target).closest('.js_product');
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            var is_break = false;

            // For each select option, check if there is only one available option aside from init option(no buy)
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                var is_single = $(el).data('single');
                if (is_single !== "true"){
                    var availOptions = []
                    $(el).find('option').each(function(){
                        if(typeof $(this).data('is_init') == 'undefined') {
                            availOptions.push($(this).val());
                        };
                    });
                    if (availOptions.length == 1) {
                        $(el).val(availOptions[0]);
                        $(el).data('single', "true");
                        hide_excluded_products(event);
                        is_break = true;
                    }
                }
            });
            if (is_break){
                return "changed";
            }
            return "done";
        }; // end auto_select

        function reset_single(event) {
            var $parent = $(event.target).closest('.js_product');
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            // For each select option, reset single data attr to false
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
                $(el).data('single', "false");
            });
        }; // end reset_single

        $('input[type="radio"].js_variant_change, select.js_variant_change').on('change', function(event) {
            reset_single(event);
            // First trigger to hide exclusions
            hide_excluded_products(event);
            // Auto select if option is only one available
            var state = "";
            while (state !== "done") {
                state = auto_select(event);
            }
        });

        //On click of Reset, Change selected to the no_buy option
        $('.reset_button').on('click', function(event) {
            event.preventDefault();
            reset_single(event);
            var $parent = $(event.target).closest('.js_product');
            _.each($parent.find('select.js_variant_change'), function (el) {
                var init_op = $(el).find('option[data-is_init=True]').val();
                $(el).val(init_op);
            });
            hide_excluded_products(event);
        }); // End reset trigger

        // Trigger the change every time Product page is loaded
        $( document ).ready(function() {
            $('input[type="radio"].js_variant_change, select.js_variant_change').trigger('change');
        });

    });

});