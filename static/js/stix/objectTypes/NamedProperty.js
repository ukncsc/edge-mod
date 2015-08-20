define([
    "dcl/dcl"
], function (declare) {
    "use strict";

    function isValueSet(value) {
        return (typeof value === "string" && value.length > 0)
            || (typeof value === "number" && isFinite(value));
    }

    function findValue(valueObj) {
        return isValueSet(valueObj) ? valueObj : (valueObj && isValueSet(valueObj["value"])) ? valueObj["value"] : null;
    }

    function formatName(name) {
        return name.replace(/(^|_)(\w)/g, function (wholeString, underscore, letter) {
            return (underscore && " ") + letter.toUpperCase();
        });
    }

    return declare(null, {
        declaredClass: "NamedProperty",
        constructor: function (name, value) {
            if (typeof name !== "string") {
                throw new TypeError("name must be a string");
            }
            this._name = formatName(name);
            this._value = findValue(value);
        },
        name: function () {
            return this._name;
        },
        value: function () {
            return this._value;
        },
        addToPropertyList: function (aPropertyList) {
            var value = this.value();
            if (value) {
                aPropertyList.push({label: this.name(), value: value});
            }
        }
    });
});
