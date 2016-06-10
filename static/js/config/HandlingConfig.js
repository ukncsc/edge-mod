define([
    "dcl/dcl",
    "knockout",
    "config/base-mongo-config"
], function (declare, ko, baseMongoConfig) {
    "use strict";

    return declare(baseMongoConfig, {
        declaredClass: "HandlingConfig",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this);
                this.handling_caveats = ko.observableArray([{"stix_value": "", "display_value": ""}]);
            }
        }),

        getConfig: function () {
            this.getData("get_sharing_groups/", "An error occurred while attempting to retrieve the Sharing Groups.");
        },

        _parseResponse: function (configText) {
            var handlingList = [];
            for (var key in configText) {
                if (configText.hasOwnProperty(key)) {
                    handlingList.push({"stix_value": key, "display_value": configText[key]})
                }
            }
            this.handling_caveats(handlingList)
        },

        addGroup: function () {
            if (this.isHandlingCaveatsFull()) {
                this.handling_caveats().push({"stix_value": "", "display_value": ""});
                this.handling_caveats.valueHasMutated();
            }
        },

        isHandlingCaveatsFull: function () {
            var arrayLength = this.handling_caveats().length
            for (var index = 0; index < arrayLength; index++) {
                if (this.handling_caveats()[index]['stix_value'] == "" || this.handling_caveats()[index]['display_value'] == "") {
                    return false
                }
            }
            return true
        },

        save: function () {
            if (this.isValid(this.handling_caveats())) {
                var configObject = this.createSimpleConfigObject(this.handling_caveats());
                var successMessage = "The sharing group mappings were successfully saved";
                var errorMessage = "An error occurred while attempting to save the sharing groups configuration";
                this.saveData("set_sharing_groups/", configObject, successMessage, errorMessage);
            } else {
                this.createErrorModal("All Handling Caveat mappings must be non-null pairs of strings.")
            }
        },

        isValid: function (handlingCaveatArray) {
            var arrayLength = handlingCaveatArray.length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.isValidString(handlingCaveatArray[index]['stix_value']) == false ||
                    this.isValidString(handlingCaveatArray[index]['display_value']) == false)
                    return false
            }
            return true
        },

        isValidString: function (/*String*/ string) {
            return typeof string === "string" && string.trim().length > 0;
        },

        createSimpleConfigObject: function (handlingArray) {
            var configObject = {};
            ko.utils.arrayForEach(handlingArray, function (arrayItem) {
                configObject[arrayItem.stix_value] = arrayItem.display_value
            });
            return configObject
        }

    });
})
;
