define([
    "../../../../dcl/dcl",
    "knockout",
    "ind-build/indicator-builder-shim",
    "ind-build/tests/unit/mock/mock-messages"
], function (declare, ko, indicator_builder, Messages) {
    "use strict";

    var MOCKAbstractMassObservable = declare(null, {
        declaredClass: "AbstractMassObservable",
        constructor: function () {
            this.objectValues = ko.observable();
            this.getObjectValuesArray = ko.observableArray();
        },

        doValidation: function () {
            return new Messages()
        },
        bulkSave: function () {
            var items = [];
            var objectValuesCount = (this.getObjectValuesArray() || []).length;
            for (var i = 0; i < objectValuesCount; i++) {
                items[i] = this.save(i);
            }
            return items;
        }
    });

    indicator_builder.AbstractMassObservable = MOCKAbstractMassObservable;

    return MOCKAbstractMassObservable;
});
