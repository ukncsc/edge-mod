define([
    "dcl/dcl",
    "knockout",
    "./StixObject",
    "kotemplate!root-obs:./templates/root-Observable.html",
    "kotemplate!observables:./templates/Observables.html",
    "kotemplate!related-observables:./templates/related-Observables.html"
], function (declare, ko, StixObject) {
    "use strict";

    return declare(StixObject, {
        constructor: function (data, stixPackage) {
            this.type = ko.computed(function () {
                return stixPackage.safeGet(this.data(), "object.properties.xsi:type");
            }, this);
            this.properties = ko.computed(function () {
                var propertyList = [];
                var properties = stixPackage.safeGet(this.data(), "object.properties");
                ko.utils.objectForEach(properties, function (name, value) {
                    if (name !== "xsi:type" && typeof value === "string" && value.length > 0) {
                        propertyList.push({label: name, value: value});
                    }
                });
                return propertyList;
            }, this);
        }
    });
});
