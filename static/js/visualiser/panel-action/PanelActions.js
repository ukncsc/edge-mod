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
        show_check: function (type, rel_type) {
            var result = false;
            ko.utils.arrayForEach(this.actions(), function (action) {
                if (action.applies_to_link()(type, rel_type)) {
                    result = true;
                }
            });

            return result;
        }
    })
});
