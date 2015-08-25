define([
    "dcl/dcl",
    "knockout",
    "./StixObjectTLP",
    "kotemplate!root-ttp:./templates/root-TTP.html",
    "kotemplate!list-ttp:./templates/list-TTPs.html"
], function (declare, ko, StixObjectTLP) {
    "use strict";

    return declare(StixObjectTLP, {
        constructor: function (data, stixPackage) {
            this.target = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "victim_targeting.identity.name");
            }, this);
            this.attackPatterns = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "behavior.attack_patterns", "title");
            }, this);
            this.malwareInstances = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "behavior.malware_instances", "types.0.value");
            }, this);
            this.intendedEffects = ko.computed(function () {
                return stixPackage.safeListGet(this.data(), "intended_effects", "value.value");
            }, this);
            this.relatedTTPs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_ttps.ttps", "ttp.idref");
            }, this);
        }
    });
});
