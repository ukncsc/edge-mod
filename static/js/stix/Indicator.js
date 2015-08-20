define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!root-ind:./templates/root-Indicator.html",
    "kotemplate!leveraged-TTPs:./templates/leveraged-TTPs.html",
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
            this.compositeIndicatorComposition = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "composite_indicator_expression.operator");
            }, this);
            this.compositeIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "composite_indicator_expression.indicators", "idref");
            }, this);
            this.observable = ko.computed(function () {
                var id = stixPackage.safeGet(this.data(), "observable.idref");
                return id ? stixPackage.findByStringId(id) : null;
            }, this);
            this.composition = ko.computed(function () {
                var observable = this.observable();
                return observable ? stixPackage.safeGet(observable.data(), "observable_composition.operator") : null;
            }, this);
            this.observables = ko.computed(function () {
                var observable = this.observable();
                return observable ? stixPackage.safeReferenceArrayGet(observable.data(), "observable_composition.observables", "idref") : null;
            }, this);
            this.relatedIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_indicators.related_indicators", "indicator.idref");
            }, this);
            this.indicatedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "indicated_ttps", "ttp.idref");
            }, this);
            this.suggestedCOAs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "suggested_coas.suggested_coas", "course_of_action.idref");
            }, this);
        }
    });
});
