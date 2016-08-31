define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
], function (declare, ko, Modal) {
    "use strict";

    return declare(Modal, {
        declaredClass: "CatalogHandlingModal",
        constructor: function (options) {
            this.items = ko.observableArray(options["handlingCaveats"]);
        },

        toggle: function (item) {
            if (this.isSelected(item)) {
                this.items.remove(item);
            } else {
                this.items.push(item)
            }
        },

        isSelected: function (item) {
            return this.items.indexOf(item) > -1;
        }
    });
});
