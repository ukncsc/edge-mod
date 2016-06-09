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
                this.handling_caveats = ko.observableArray([]);
            }
        }),

        getConfig: function () {
            this.getData("get_sharing_groups/", "An error occurred while attempting to retrieve the Sharing Groups.");
        },

        _parseResponse: function (configText) {
            var handlingList = [];
            for (var key in configText) {
                if (configText.hasOwnProperty(key)) {
                    handlingList.push({"group": key, "label": configText[key]})
                }
            }
            this.handling_caveats(handlingList)
        },

        addGroup: function () {
            var isFull = this.checkHandlingCaveatsFull();
            if (isFull) {
                this.handling_caveats().push({"group": "", "label": ""});
                this.handling_caveats.valueHasMutated();
            }
        },

        checkHandlingCaveatsFull: function () {
            var arrayLength = this.handling_caveats().length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.handling_caveats()[index]['group'] == "" && this.handling_caveats()[index]['label'] =="") {
                    return false
                }
            }
            return true
        },

        save: function () {
            var configObject = this.createSimpleConfigObject(this.handling_caveats());
            var successMessage = "The sharing group mappings were successfully saved";
            var errorMessage = "An error occurred while attempting to save the sharing groups configuration";
            this.saveData("set_sharing_groups/", configObject, successMessage, errorMessage);
        },

        createSimpleConfigObject: function (handlingArray) {
            var configObject = {};
            handlingArray.forEach(function (arrayItem) {
                configObject[arrayItem.group] = arrayItem.label
            });
            return configObject
        }

    });
});
