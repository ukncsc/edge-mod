define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObjectTLP",
    "kotemplate!root-ind:./templates/root-Indicator.html",
    "kotemplate!flat-ind:./templates/flat-Indicator.html",
    "kotemplate!list-ind:./templates/list-Indicators.html"
], function (declare, ko, ReviewValue, StixObjectTLP) {
    "use strict";

    var KILL_CHAIN_PHASES = window["killChainPhases"];

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
            }, this, this.DEFER_EVALUATION);
            this.observable = ko.computed(function () {
                var id = stixPackage.safeGet(this.data(), "observable.idref");
                return id ? stixPackage.findByStringId(id) : null;
            }, this, this.DEFER_EVALUATION);
            this.composition = ko.computed(function () {
                var observable = this.observable();
                return observable ? stixPackage.safeValueGet(this.id(), observable.data(), "observable_composition.operator") : new ReviewValue(null);
            }, this, this.DEFER_EVALUATION);
            this.observables = ko.computed(function () {
                var observable = this.observable();
                var observableList = new ReviewValue(null);
                if (observable) {
                    observableList = stixPackage.safeReferenceArrayGet(this.id(), observable.data(), "observable_composition.observables", "idref", "observables");
                    if (observableList.isEmpty()) {
                        observableList = new ReviewValue([observable], observableList.state(), observableList.message());
                    }
                }
                return observableList;
            }, this, this.DEFER_EVALUATION);
            this.relatedIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "related_indicators.related_indicators", "indicator.idref", "related_indicators");
            }, this, this.DEFER_EVALUATION);
            this.indicatedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "indicated_ttps", "ttp.idref");
            }, this, this.DEFER_EVALUATION);
            this.suggestedCOAs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "suggested_coas.suggested_coas", "course_of_action.idref", "suggested_coas");
            }, this, this.DEFER_EVALUATION);
        }
    });
});
