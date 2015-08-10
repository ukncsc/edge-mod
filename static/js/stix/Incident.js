define(["dcl/dcl", "knockout", "./StixObject"], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.status = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "status.value");
            }, this);
            this.reporter = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "reporter.identity.name");
            }, this);
            this.confidence = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "confidence.value.value");
            }, this);
            this.responders = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "responders", "identity.name");
            }, this);
            this.intendedEffects = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "intended_effects", "value.value");
            }, this);
            this.discoveryMethods = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "discovery_methods");
            }, this);
            this.impactAssessment = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "impact_assessment.effects");
            }, this);
            this.leveragedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "leveraged_ttps.ttps", "ttp.idref");
            }, this);
            this.relatedIncidents = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_incidents.incidents", "incident.idref");
            }, this);
            this.relatedIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_indicators.indicators", "indicator.idref");
            }, this);
            this.relatedObservables = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_observables.observables", "observable.idref");
            }, this);
        }
    });
});
