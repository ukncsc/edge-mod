define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObjectTLP",
    "kotemplate!root-act:./templates/root-ThreatActor.html",
    "kotemplate!flat-act:./templates/flat-ThreatActor.html",
    "kotemplate!list-act:./templates/list-ThreatActors.html"
], function (declare, ko, ReviewValue, StixObjectTLP) {
    "use strict";

    return declare(StixObjectTLP, {
        constructor: function (data, stixPackage) {
            this.name = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "identity.name");
            }, this);
            this.types = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), data, "types", "value.value");
            }, this);
            this.motivations = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), data, "motivations", "value.value");
            }, this);
            this.sophistications = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), data, "sophistications", "value.value");
            }, this);
            this.intendedEffects = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), data, "intended_effects", "value.value");
            }, this);
            this.operationalSupports = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), data, "planning_and_operational_supports", "value.value");
            }, this);
            this.observedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), data, "observed_ttps.ttps", "ttp.idref");
            }, this, this.DEFER_EVALUATION);
            this.associatedActors = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), data, "associated_actors.threat_actors", "threat_actor.idref");
            }, this, this.DEFER_EVALUATION);
            this.associatedCampaigns = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), data, "associated_campaigns.campaigns", "campaign.idref");
            }, this, this.DEFER_EVALUATION);
        }
    });
});
