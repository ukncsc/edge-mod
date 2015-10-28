define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!common-fields-TLP:./templates/commonTLP.html"
], function (declare, ko, StixObject) {
    "use strict";

    function simpleItem (item) {
        return item;
    }

    function findByXsiType (markingStructures, xsiType, valueKey) {
        return (ko.utils.arrayMap(ko.utils.arrayFilter(markingStructures, function (item) {
            return item["xsi:type"].split(":", 2)[1] === xsiType;
        }), function (item) {
            return item[valueKey];
        })).join(", ");
    }

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            var markingStructures = stixPackage.safeArrayGet(this.data(), "handling.0.marking_structures", simpleItem, this)
                || stixPackage.safeArrayGet(stixPackage.header(), "handling.0.marking_structures", simpleItem, this);

            this.tlp = ko.computed(function () {
                return findByXsiType(markingStructures, "TLPMarkingStructureType", "color");
            }, this);
            this.handlingCaveats = ko.computed(function () {
                return findByXsiType(markingStructures, "SimpleMarkingStructureType", "statement");
            }, this);
            this.termsOfUse = ko.computed(function () {
                return findByXsiType(markingStructures, "TermsOfUseMarkingStructureType", "terms_of_use");
            }, this);
        }
    });
});
