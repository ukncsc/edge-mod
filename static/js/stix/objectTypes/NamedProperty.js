define([
    "dcl/dcl",
    "knockout",
    "../ReviewValue"
], function (declare, ko, ReviewValue) {
    "use strict";

    function formatName(name) {
        return name.replace(/(^|_)(\w)/g, function (wholeString, underscore, letter) {
            return (underscore && " ") + letter.toUpperCase();
        });
    }

    var NamedProperty = declare(null, {
        declaredClass: "NamedProperty",
        constructor: function (name, value) {
            if (typeof name !== "string") {
                throw new TypeError("name must be a string");
            }
            this.name = ko.observable(formatName(name));
            this.value = value instanceof ReviewValue ? ko.observable(value) : ko.observable(new ReviewValue(value));
        }
    });
    NamedProperty.addToPropertyList = function (aPropertyList, name, value) {
        var namedProperty = new NamedProperty(name, value);
        var realValue = namedProperty.value();
        if (!(realValue.isEmpty())) {
            aPropertyList.push({label: namedProperty.name, value: namedProperty.value});
        }
    };
    NamedProperty.removeFromPropertyList = function (aPropertyList, name) {
        var nameIdx = -1;
        var searchFor = formatName(name);
        ko.utils.arrayForEach(aPropertyList, function (namedProperty, idx) {
            if (nameIdx === -1 && namedProperty.label() === searchFor) {
                nameIdx = idx;
            }
        });
        if (nameIdx > 0) {
            aPropertyList.splice(nameIdx, 1);
        } else if (nameIdx === 0) {
            aPropertyList.shift();
        }
    };
    return NamedProperty;
});
