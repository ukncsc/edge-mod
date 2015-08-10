define(["dcl/dcl", "knockout", "./StixObject"], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.intendedEffects = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "intended_effects", "value.value");
            }, this);
        }
    });
});
