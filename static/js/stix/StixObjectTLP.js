define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObject",
    "text!config-service",
    "kotemplate!common-fields-TLP:./templates/commonTLP.html"
], function (declare, ko, ReviewValue, StixObject, configService) {
    "use strict";

    var config = Object.freeze(JSON.parse(configService));
    var sharing_groups = config.sharing_groups;

    function simpleItem(item) {
        return item;
    }

    function checkIsHandlingCaveat(item, valueKey) {
        if (item.hasOwnProperty("marking_model_name")) {
            return sharing_groups[item["statement"]]
        } else {
            return item[valueKey];
        }
    }

    function findByXsiType(markingStructures, xsiType, valueKey, validation) {
        var value = (ko.utils.arrayMap(ko.utils.arrayFilter(markingStructures, function (item) {
            return item["xsi:type"].split(":", 2)[1] === xsiType;
        }), function (item) {
            return checkIsHandlingCaveat(item, valueKey)
        })).join(", ");
        return new ReviewValue(value, validation.state, validation.message);
    }

    return declare(StixObject, {
            constructor: function (data, stixPackage) {
                var markingStructures = stixPackage.safeArrayGet(this.data(), "handling.0.marking_structures", simpleItem, this)
                    || stixPackage.safeArrayGet(stixPackage.header(), "handling.0.marking_structures", simpleItem, this);
                this.tlp = ko.computed(function () {
                    var validation = stixPackage.validations().findByProperty(this.id(), "tlp");
                    return findByXsiType(markingStructures, "TLPMarkingStructureType", "color", validation);
                }, this);
                this.marking = ko.computed(function () {
                    var validation = stixPackage.validations().findByProperty(this.id(), "marking");
                    return findByXsiType(markingStructures, "SimpleMarkingStructureType", "statement", validation);
                }, this);
                this.termsOfUse = ko.computed(function () {
                    var validation = stixPackage.validations().findByProperty(this.id(), "termsOfUse");
                    return findByXsiType(markingStructures, "TermsOfUseMarkingStructureType", "terms_of_use", validation);
                }, this);
            }
        }
    );
})
;
