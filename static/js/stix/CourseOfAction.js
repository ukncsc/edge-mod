define([
    "dcl/dcl",
    "knockout",
    "./StixObjectTLP",
    "kotemplate!root-coa:./templates/root-COA.html",
    "kotemplate!list-coa:./templates/list-COAs.html"
], function (declare, ko, StixObjectTLP) {
    "use strict";

    return declare(StixObjectTLP, {
        constructor: function (data, stixPackage) {
            this.stage = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "stage.value");
            }, this);
            this.type = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "type.value");
            }, this);
            this.objective = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "objective.description");
            }, this);
            this.impact = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "impact.description");
            }, this);
            this.efficacy = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "efficacy.description");
            }, this);
            this.cost = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), this.data(), "cost.description");
            }, this);
            this.properties = ko.computed(function () {
                return ko.utils.arrayFilter([
                    {label: "Stage", value: this.stage().value()},
                    {label: "Type", value: this.type().value()},
                    {label: "Objective", value: this.objective().value()},
                    {label: "Impact", value: this.impact().value()},
                    {label: "Efficacy", value: this.efficacy().value()},
                    {label: "Cost", value: this.cost().value()}
                ], function (property) {
                    return typeof property.value === "string" && property.value.length > 0;
                });
            }, this);
            this.relatedCOAs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.data(), "related_coas.coas", "course_of_action.idref");
            }, this);
        }
    });
});
