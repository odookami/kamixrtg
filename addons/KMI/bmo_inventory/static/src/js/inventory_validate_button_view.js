odoo.define('bmo_inventory.InventoryApprovelView', function (require) {
    "use strict";

    var InventoryApprovelController = require('bmo_inventory.InventoryApprovelController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var InventoryValidationView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: InventoryApprovelController
        })
    });

    viewRegistry.add('inventory_validate_button', InventoryApprovelView);

});
