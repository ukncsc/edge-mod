define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObject",
    "kotemplate!common-fields-TLP:./templates/commonTLP.html"
], function (declare, ko, ReviewValue, StixObject) {
    "use strict";

    function simpleItem (item) {
        return item;
    }

    function isBlankString(value) {
        return !((typeof value === "string" || value instanceof String) && value.length > 0);
    }

    function validate (xsiType, value) {
        var validation = { state: ReviewValue.State.OK, message: null };
        if (xsiType === "TLPMarkingStructureType" && isBlankString(value)) {
            validation.state = ReviewValue.State.ERROR;
            validation.message = "TLP missing";
        }
        return validation;
    }

    function findByXsiType (markingStructures, xsiType, valueKey) {
        var value = (ko.utils.arrayMap(ko.utils.arrayFilter(markingStructures, function (item) {
            return item["xsi:type"].split(":", 2)[1] === xsiType;
        }), function (item) {
            return item[valueKey];
        })).join(", ");
        // TODO: pull validation messages from the server (somehow!)
        var validation = validate(xsiType, value);
        return new ReviewValue(value, validation.state, validation.message);
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
