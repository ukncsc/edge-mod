define([
    "../../dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    return declare(null, {
        declaredClass: "PanelActions",
        constructor: function () {
            this.actions = ko.observableArray([])
        },
        show_reference_check: function (type) {
            var result = false;
            ko.utils.arrayForEach(this.actions(), function (action) {
                if (action.applies_to_references()(type)) {
                    result = true;
                }
            })

            return result;
        },
        show_referenced_by_check: function (type) {
            var result = false;
            ko.utils.arrayForEach(this.actions(), function (action) {
                if (action.applies_to_referenced_by()(type)) {
                    result = true;
                }
            })

            return result;
        }
    })
});
