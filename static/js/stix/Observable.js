define(["dcl/dcl", "knockout", "./StixObject"], function (declare, ko, StixObject) {
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
