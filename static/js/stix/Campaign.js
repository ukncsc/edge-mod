define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObjectTLP",
    "kotemplate!root-cam:./templates/root-Campaign.html",
    "kotemplate!flat-cam:./templates/flat-Campaign.html",
    "kotemplate!list-cam:./templates/list-Campaigns.html"
], function (declare, ko, ReviewValue, StixObjectTLP) {
    "use strict";

    return declare(StixObjectTLP, {
        constructor: function (data, stixPackage) {
            this.status = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(),"status.value");
            }, this);
            this.intendedEffects = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), this.data(), "intended_effects", "value.value");
            }, this);
            this.names = ko.computed(function () {
                return stixPackage.safeListGet(this.id(), this.data(), "names.names", ".");
            }, this);
            this.relatedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "related_ttps.ttps", "ttp.idref");
            }, this, this.DEFER_EVALUATION);
            this.associatedCampaigns = ko.computed(function () {
             return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "associated_campaigns.campaigns", "campaign.idref");
             }, this, this.DEFER_EVALUATION);
            this.relatedIncidents = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "related_incidents.incidents", "incident.idref");
            }, this, this.DEFER_EVALUATION);
            this.relatedIndicators = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "related_indicators.indicators", "indicator.idref");
            }, this, this.DEFER_EVALUATION);
            this.relatedActors = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), this.data(), "attribution.0.threat_actors", "threat_actor.idref");
            }, this, this.DEFER_EVALUATION);
        }
    });
});
