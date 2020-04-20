odoo.define('luonto_product.ProductConfiguratorFormControllerLuonto', function (require) {
'use strict';
var ProductConfiguratorFormController = require('sale.ProductConfiguratorFormController');

var ProductConfiguratorFormControllerLuonto = ProductConfiguratorFormController.include({
    custom_events: _.extend({}, ProductConfiguratorFormController.prototype.custom_events, {
        field_changed: '_onFieldChanged',
    }),

    /**
     * Hides the add button and shows the dummy button
     *
     * @private
     * @param {Onchange} event
     */
    _onFieldChanged: function (event) {
        this.$el.parents('.modal').find('.o_sale_product_configurator_add').hide();
//        this.$el.parents('.modal').find('.o_dummy_add_button').removeClass('o_button_hidden');
        this._super.apply(this, arguments);
    },

});

return ProductConfiguratorFormControllerLuonto;

});
