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
                this.handling_caveats = ko.observable();
            }
        }),

        getConfig: function () {
            this.getData("get_sharing_groups/", "An error occurred while attempting to retrieve the Sharing Groups.");
        },

        _parseResponse: function (configText) {
            var handlingList = []
            for (var key in configText) {
                if (configText.hasOwnProperty(key)) {
                    handlingList.push({"group": key, "label": configText[key]})
                }
            }
            this.handling_caveats(handlingList)
        },

        addGroup: function () {
            //check no empty ones in list already
        },

        save: function () {
            var configObject = this.createSimpleConfigObject(this.handling_caveats());
            var successMessage = "The sharing group mappings were successfuly saved";
            var errorMessage = "An error occurred while attempting to save the sharing groups configuration"
            this.saveData("set_sharing_groups/", configObject, successMessage, errorMessage);
        },

        createSimpleConfigObject: function (handlingArray) {
            var configObject = {};
            handlingArray.forEach(function (arrayItem) {
                configObject[arrayItem.group]= arrayItem.label
            });
            return configObject
        }

    });
});
