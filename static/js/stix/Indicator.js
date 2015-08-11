define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!root-ind:./templates/root-Indicator.html",
    "kotemplate!related-indicators:./templates/related-Indicators.html"
], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.producer = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "producer.identity.name");
            }, this);
            this.confidence = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "confidence.value.value");
            }, this);
            this.indicatorTypes = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "indicator_types");
            }, this);
            this.observable = ko.computed(function () {
                return stixPackage.findById(
                    stixPackage.safeGet(this.data(), "observable.idref")
                )
            }, this);
            this.composition = ko.computed(function () {
                return stixPackage.safeGet(this.observable().data(), "observable_composition.operator");
            }, this);
            this.observables = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.observable().data(), "observable_composition.observables", "idref");
            }, this);
            this.relatedIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_indicators.related_indicators", "indicator.idref");
            }, this);
            this.suggestedCOAs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "suggested_coas.suggested_coas", "course_of_action.idref");
            }, this);
        }
    });
});
