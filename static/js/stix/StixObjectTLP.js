define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!common-fields-TLP:./templates/commonTLP.html"
], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.tlp = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "handling.0.marking_structures.0.color")
                    || stixPackage.safeGet(stixPackage.header(), "handling.0.marking_structures.0.color");
            }, this);
        }
    });
});
