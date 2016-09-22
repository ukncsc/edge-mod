define([
    "dcl/dcl",
    "knockout",
    "../ReviewValue"
], function (declare, ko, ReviewValue) {
    "use strict";

    function asReviewValue(rawValue) {
        return rawValue instanceof ReviewValue
            ? rawValue
            : new ReviewValue(rawValue);
    }

    function findValue(rawValue) {
        return asReviewValue(rawValue).value;
    }

    function formatName(name) {
        if (typeof name !== "string") {
            throw new TypeError("name must be a string");
        }
        return name.replace(/(^|_)(\w)/g, function (wholeString, underscore, letter) {
            return (underscore && " ") + letter.toUpperCase();
        });
    }

    var NamedProperty = declare(null, {
        declaredClass: "NamedProperty",
        constructor: function (name, value) {
            this.name = ko.observable(formatName(findValue(name)));
            this.value = ko.observable(asReviewValue(value));
        }
    });
    NamedProperty.addToPropertyList = function (aPropertyList, name, value) {
        if (!(aPropertyList instanceof Array)) {
            throw new TypeError("aPropertyList must be an array");
        }
        var namedProperty = new NamedProperty(name, value);
        var realValue = namedProperty.value();
        if (!(realValue.isEmpty)) {
            aPropertyList.push({label: namedProperty.name, value: namedProperty.value});
        }
    };
    NamedProperty.removeFromPropertyList = function (aPropertyList, name) {
        if (!(aPropertyList instanceof Array)) {
            throw new TypeError("aPropertyList must be an array");
        }
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
