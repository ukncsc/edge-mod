define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObjectTLP",
    "kotemplate!root-ind:./templates/root-Indicator.html",
    "kotemplate!list-ind:./templates/list-Indicators.html"
], function (declare, ko, ReviewValue, StixObjectTLP) {
    "use strict";

    var KILL_CHAIN_PHASES = ((!(typeof window === "undefined") && window) || {})["killChainPhases"] || {
            // fallback list to facilitate unit testing
            "stix:TTP-79a0e041-9d5f-49bb-ada4-8322622b162d": "Delivery",
            "stix:TTP-af1016d6-a744-4ed7-ac91-00fe2272185a": "Reconnaissance",
            "stix:TTP-786ca8f9-2d9a-4213-b38e-399af4a2e5d6": "Actions on Objectives",
            "stix:TTP-445b4827-3cca-42bd-8421-f2e947133c16": "Weaponization",
            "stix:TTP-d6dc32b9-2538-4951-8733-3cb9ef1daae2": "Command and Control",
            "stix:TTP-f706e4e7-53d8-44ef-967f-81535c9db7d0": "Exploitation",
            "stix:TTP-e1e4e3f7-be3b-4b39-b80a-a593cfd99a4f": "Installation"
        };

    return declare(StixObjectTLP, {
        constructor: function (data, stixPackage) {
            this.producer = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "producer.identity.name", "producer");
            }, this);
            this.confidence = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "confidence.value.value", "confidence");
            }, this);
            this.indicatorTypes = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), this.data(), "indicator_types");
            }, this);
            this.killChainPhase = ko.computed(function () {
                var killChainPhase = stixPackage.safeValueGet(this.id(), this.data(), "kill_chain_phases.kill_chain_phases.0.phase_id", "phase_id");
                if (!(killChainPhase.isEmpty())) {
                    // create a new ReviewValue with the name rather than the id
                    var phaseId = killChainPhase.value();
                    if (KILL_CHAIN_PHASES.hasOwnProperty(phaseId)) {
                        killChainPhase = new ReviewValue(
                            KILL_CHAIN_PHASES[phaseId],
                            killChainPhase.state(),
                            killChainPhase.message()
                        );
                    }
                }
                return killChainPhase;
            }, this);
            this.compositeIndicatorComposition = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "composite_indicator_expression.operator");
            }, this);
            this.compositeIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "composite_indicator_expression.indicators", "idref");
            }, this);
            this.observable = ko.computed(function () {
                var id = stixPackage.safeGet(this.data(), "observable.idref");
                return id ? stixPackage.findByStringId(id) : null;
            }, this);
            this.composition = ko.computed(function () {
                var observable = this.observable();
                return observable ? stixPackage.safeValueGet(this.id(), observable.data(), "observable_composition.operator") : null;
            }, this);
            this.observables = ko.computed(function () {
                var observable = this.observable();
                var observableList = null;
                if (observable) {
                    observableList = stixPackage.safeReferenceArrayGet(this.id(), observable.data(), "observable_composition.observables", "idref", "observables");
                    if (observableList.isEmpty()) {
                        observableList = new ReviewValue([observable], observableList.state(), observableList.message());
                    }
                }
                return observableList;
            }, this);
            this.relatedIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "related_indicators.related_indicators", "indicator.idref", "related_indicators");
            }, this);
            this.indicatedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "indicated_ttps", "ttp.idref");
            }, this);
            this.suggestedCOAs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "suggested_coas.suggested_coas", "course_of_action.idref", "suggested_coas");
            }, this);
        }
    });
});
