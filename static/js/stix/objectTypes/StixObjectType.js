define([
    "dcl/dcl",
    "knockout"
], function (declare, ko) {
    "use strict";

    function isValueSet(value) {
        return (typeof value === "string" && value.length > 0)
            || (typeof value === "number" && isFinite(value));
    }

    function findValue(valueObj) {
        return isValueSet(valueObj) ? valueObj : (valueObj && isValueSet(valueObj["value"])) ? valueObj["value"] : null;
    }

    function formatName(name) {
        return name.replace(/(^|_)(\w)/g, function(wholeString, underscore, letter) {
            return (underscore && " ") + letter.toUpperCase();
        });
    }

    function extractSimpleProperty(name, rawValue) {
        var simpleProperty = null;
        if (name !== "xsi:type") {
            var value = findValue(rawValue);
            if (value) {
                simpleProperty = {label: formatName(name), value: value};
            }
        }
        return simpleProperty;
    }

    return declare(null, {
        declaredClass: "StixObjectType",
        constructor: function (data, stixPackage) {
            this.data = data;
            this.stixPackage = stixPackage;
        },
        properties: function () {
            var propertyList = [];
            ko.utils.objectForEach(this.data, function (name, value) {
                var simpleProperty = extractSimpleProperty(name, value);
                if (simpleProperty) {
                    propertyList.push(simpleProperty);
                }
            });
            if (this.data && this.data["custom_properties"] instanceof Array) {
                ko.utils.arrayForEach(this.data["custom_properties"], function (property) {
                    var simpleProperty = extractSimpleProperty(property.name, property.value);
                    if (simpleProperty) {
                        propertyList.push(simpleProperty);
                    }
                });
            }
            return propertyList;
        }
    });
});
