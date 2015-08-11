define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!root-ttp:./templates/root-TTP.html",
    "kotemplate!leveraged-ttps:./templates/leveraged-TTPs.html"
], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.intendedEffects = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "intended_effects", "value.value");
            }, this);
        }
    });
});
