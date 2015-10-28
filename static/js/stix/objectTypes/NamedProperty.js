define([
    "dcl/dcl",
    "../../common/ValidationInfo"
], function (declare, ValidationInfo) {
    "use strict";

    function isValueSet(value) {
        return (typeof value === "string" && value.length > 0)
            || (typeof value === "number" && isFinite(value))
            || (typeof value === "boolean");
    }

    function findValue(valueObj) {
        return isValueSet(valueObj) ? valueObj : (valueObj && isValueSet(valueObj["value"])) ? valueObj["value"] : null;
    }

    function formatName(name) {
        return name.replace(/(^|_)(\w)/g, function (wholeString, underscore, letter) {
            return (underscore && " ") + letter.toUpperCase();
        });
    }

    var NamedProperty = declare(null, {
        declaredClass: "NamedProperty",
        constructor: function (name, value, validation) {
            var useName = findValue(name);
            if (typeof useName !== "string") {
                throw new TypeError("name must be a string: " + name);
            }
            this._name = formatName(useName);
            this._value = findValue(value);
            this._validation = new ValidationInfo(validation);
        },
        name: function () {
            return this._name;
        },
        value: function () {
            return this._value;
        },
        validation: function () {
            return this._validation;
        }
    });
    NamedProperty.addToPropertyList = function (aPropertyList, name, value, validation) {
        var namedProperty = new NamedProperty(name, value, validation);
        var realValue = namedProperty.value();
        if (realValue) {
            aPropertyList.push({
                label: namedProperty.name(),
                value: realValue,
                validation: namedProperty.validation()
            });
        }
    };
    return NamedProperty;
});
