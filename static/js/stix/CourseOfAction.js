define([
    "dcl/dcl",
    "knockout",
    "./ReviewValue",
    "./StixObjectTLP",
    "kotemplate!root-coa:./templates/root-COA.html",
    "kotemplate!flat-coa:./templates/flat-COA.html",
    "kotemplate!list-coa:./templates/list-COAs.html"
], function (declare, ko, ReviewValue, StixObjectTLP) {
    "use strict";

    return declare(StixObjectTLP, {
        constructor: function (data, stixPackage) {
            this.stage = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "stage.value");
            }, this);
            this.type = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "type.value");
            }, this);
            this.objective = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "objective.description");
            }, this);
            this.impact = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "impact.description");
            }, this);
            this.efficacy = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "efficacy.description");
            }, this);
            this.cost = ko.computed(function () {
                return stixPackage.safeValueGet(this.id(), data, "cost.description");
            }, this);
            this.properties = ko.computed(function () {
                return ko.utils.arrayFilter([
                    {label: "Stage", value: ko.observable(this.stage())},
                    {label: "Type", value: ko.observable(this.type())},
                    {label: "Objective", value: ko.observable(this.objective())},
                    {label: "Impact", value: ko.observable(this.impact())},
                    {label: "Efficacy", value: ko.observable(this.efficacy())},
                    {label: "Cost", value: ko.observable(this.cost())}
                ], function (property) {
                    var value = property.value();
                    return value instanceof ReviewValue && !(value.isEmpty);
                });
            }, this);
            this.relatedCOAs = ko.computed(function () {
                return stixPackage.safeReferenceArrayGet(this.id(), data, "related_coas.coas", "course_of_action.idref");
            }, this, this.DEFER_EVALUATION);
        }
    });
});
