define([
    "dcl/dcl",
    "knockout",
    "../ReviewValue",
    "./NamedProperty"
], function (declare, ko, ReviewValue, NamedProperty) {
    "use strict";

    return declare(null, {
        declaredClass: "StixObjectType",
        constructor: function (id, data, stixPackage) {
            this.id = id;
            this.data = data;
            this.stixPackage = stixPackage;
        },
        properties: function () {
            var propertyList = [];
            if (this.data instanceof Object) {
                Object.keys(this.data).forEach(function (name) {
                    if (name === "xsi:type" || name === "custom_properties") {
                        return;
                    }
                    var reviewValue = this.stixPackage.safeValueGet(this.id, this.data, name);
                    NamedProperty.addToPropertyList(propertyList, name, reviewValue);
                }.bind(this));
                var customProperties = this.stixPackage.safeGet(this.data, "custom_properties");
                if (customProperties instanceof Array) {
                    ko.utils.arrayForEach(customProperties, function (property) {
                        if (property.name === "xsi:type") {
                            return;
                        }
                        NamedProperty.addToPropertyList(propertyList, property.name, property.value);
                    });
                }
            }
            return propertyList;
        }
    });
});
