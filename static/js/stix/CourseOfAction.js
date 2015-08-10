define(["dcl/dcl", "knockout", "./StixObject"], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.stage = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "stage.value");
            }, this);
            this.type = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "type.value");
            }, this);
            this.objective = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "objective.description");
            }, this);
            this.impact = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "impact.description");
            }, this);
            this.efficacy = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "efficacy.description");
            }, this);
            this.cost = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "cost.description");
            }, this);
            this.properties = ko.computed(function () {
                return ko.utils.arrayFilter([
                    {label: "stage", value: this.stage()},
                    {label: "type", value: this.type()},
                    {label: "objective", value: this.objective()},
                    {label: "impact", value: this.impact()},
                    {label: "efficacy", value: this.efficacy()},
                    {label: "cost", value: this.cost()}
                ], function (property) {
                    return typeof property.value === "string" && property.value.length > 0;
                });
            }, this);
        }
    });
});
