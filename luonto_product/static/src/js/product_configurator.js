odoo.define('luonto_product.ProductConfiguratorFormRendererLuonto', function (require) {
'use strict';
var ProductConfiguratorFormRenderer = require('sale.ProductConfiguratorFormRenderer');

var ProductConfiguratorFormRendererLuonto = ProductConfiguratorFormRenderer.include({
    /**
     * @override
     */
    events: _.extend({}, ProductConfiguratorFormRenderer.prototype.events, {
        'click .reset_button': '_resetProdConfig',
    }),

    /**
     * Shows the add button and hides the dummy button
     *
     * @private
     * @param configuratorHtml
     */
    renderConfigurator: function (configuratorHtml) {
        this._super.apply(this, arguments);
        this.$el.parents('.modal').find('.o_dummy_add_button').addClass('o_button_hidden');
        this.$el.parents('.modal').find('.o_sale_product_configurator_add').show();

    },

    /**
     * Hides the excluded products based on js computation
     *
     * @private
     * @param {div.js_product} $parent
     */
    _hideExcludedProducts: function ($parent) {
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

        for (var attr of attr_values) {
            var hide = flat_ex[attr]
            for (var h of hide) {
                $('input[data-value_id="'+ h +'"]').remove();
                $('option[data-value_id="'+ h +'"]').remove();
            }
        }

        var findNoBuy = no_buy_variants.some(r=> values.indexOf(r) >= 0);
        var $test_parent = $parent.parents('.modal').find('.o_sale_product_configurator_add');
        $test_parent.removeClass('stop_buy');
        if (findNoBuy) {
           $test_parent.addClass('stop_buy');
        }
    }, // End hideExcludedProducts

    /**
     * Auto selects the selection option given there is only one other option aside
     * from the Initial Option.@param {MouseClick} event
     *
     * @private
     * @param {div.js_product} $parent
     */
    _autoSelect: function ($parent) {
        var variantsValuesSelectors = [
            'input.js_variant_change:checked',
            'select.js_variant_change'
        ];

        // For each select option, check if there is only one available option aside from init option(no buy)
        _.each($parent.find(variantsValuesSelectors.join(', ')), function (el) {
            var availOptions = []
            $(el).find('option').each(function(){
                if(typeof $(this).data('is_init') == 'undefined') {
                    availOptions.push($(this).val());
                };
            });
            if (availOptions.length == 1) {
                $(el).val(availOptions[0]);
            }
        });
    }, // end auto_select

    /**
     * Resets all the selection fields.
     *
     * @private
     * @param {MouseClick} event
     */
    _resetProdConfig: function (event) {
        event.preventDefault();
        var self = this;
        var $parent = $(event.target).closest('.js_product');

        _.each($parent.find('select.js_variant_change'), function (el) {
            var init_op = $(el).find('option[data-is_init=True]').val();
            $(el).val(init_op);
        });
        self._hideExcludedProducts($parent);
    },

    /**
     * Override the _checkExclusions function to add flat exclusions.
     *
     * @private
     * @param {Array} combination the selected combination of product attribute values
     */
    _checkExclusions: function ($parent, combination) {
        this._super.apply(this, arguments);
        var self = this;

        self._hideExcludedProducts($parent);
        self._autoSelect($parent);
        self._hideExcludedProducts($parent);
    },
});

return ProductConfiguratorFormRendererLuonto;

});
