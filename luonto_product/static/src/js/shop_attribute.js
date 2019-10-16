odoo.define('website_sale.new_cart', function (require) {
"use strict";
    $("form.form-inline").addClass("pull-left");
    var cart = require('website_sale.cart');
    var web_editor_base = require('web_editor.base');
    var ajax = require("web.ajax")
    var core = require("web.core")

    web_editor_base.ready().then(function(){
        function hide_excluded_products(source_form, attr_id, event) {
            var $form = source_form;
            var values = [];
            var attr_id = parseInt(attr_id);

            var $parent = $(event.target).closest('.js_product');
            var productTemplateId = parseInt($parent.find('.product_template_id').val());

            var product_exclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').exclusions
//            console.log(product_exclusions)

            // Grab the values that are currently selected
            var values = [];
//            console.log("NEXT LOG: ")
            var variantsValuesSelectors = [
                'input.js_variant_change:checked',
                'select.js_variant_change'
            ];
            _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
            values.push(+$(el).val());
            });

            $('input').parent().parent().show();
            $('option').show();
//            $('input').parent().parent().removeClass('hidden');
//            $('option').removeClass('hidden');

//            $('input').parent().parent().unwrap(".hide_ex");
//            $('option').unwrap(".hide_ex");
//            $('option').wrap("<div class='hide_ex'></span>");

            for (var val of values) {
                var to_hide = product_exclusions[val]
                // Hide all related attribute values
                for (var h of to_hide) {
                    $('input[value="'+ h +'"]').parent().parent().hide();
                    $('option[value="'+ h +'"]').hide();
//                    $('input[value="'+ h +'"]').parent().parent().wrap("<span class='hide_ex'></span>");
//                    $('option[value="'+ h +'"]').wrap("<span class='hide_ex'></span>");
//                    $('input[value="'+ h +'"]').parent().parent().addClass('hidden');
//                    $('option[value="'+ h +'"]').addClass('hidden');
                }
            }
        } // End hide_excluded_products


        $('input[type="radio"].js_variant_change').on('change', function(event) {
            var $form = $(this).closest('form');
            hide_excluded_products($form, $(this).val(), event);

        });

        $('select.js_variant_change').on("change",function(event){
            var $form = $(this).closest('form');
            hide_excluded_products($form, $(this).val(), event);
        });

        // Trigger the change everytime Product page is loaded
        $( document ).ready(function() {
            $('input[type="radio"].js_variant_change, select.js_variant_change').trigger('change');
        });

    });




});