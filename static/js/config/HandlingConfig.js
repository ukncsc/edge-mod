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
                sup.call(this, "get_sharing_groups/", "An error occurred while attempting to retrieve the Sharing Groups.");
                this.handling_caveats = ko.observableArray([]);
                this.saved_handling_caveats = [];
                // The save button should only be available if there is something to save.
                // This flag tests changes to Enabled status, changes in number of Handling Caveats, and changes to stix_value and display_value of existing caveats
                this.something_to_save_trigger = ko.observable("dummy variable");
                this.something_to_save = ko.computed(function () {
                    var trigger = this.something_to_save_trigger() + "";
                    //Empty Caveats will be removed before saving. It is therefore necessary to exclude new pairs that are empty in the difference tests
                    //We need to create a JS copy to avoid changing the ko handling_caveats.
                    var current_handling_caveats = ko.toJS(this.handling_caveats);
                    current_handling_caveats = current_handling_caveats.filter(function (caveat) {
                        return caveat.stix_value || caveat.display_value
                    });

                    var stringifiedSavedHandlingArray = [];

                    if (this.savedEnabled() != this.enabled())
                        return true;
                    if (current_handling_caveats.length != this.saved_handling_caveats.length)
                        return true;

                    for (var i in this.saved_handling_caveats)
                        stringifiedSavedHandlingArray.push(JSON.stringify(this.saved_handling_caveats[i]));

                    for (var i in current_handling_caveats) {
                        var stringifiedItem = JSON.stringify({
                            stix_value: current_handling_caveats[i].stix_value,
                            display_value: current_handling_caveats[i].display_value
                        });

                        // Note  - Equality of objects method is not perfect.
                        // If the order of attributes in the object are different they will be considered different.
                        var handlingCaveatNotSaved = stringifiedSavedHandlingArray.indexOf(stringifiedItem) == -1;
                        if (handlingCaveatNotSaved)
                            return true
                    }
                    return false;
                }, this);
            }
        }),
        _createHandlingCaveat: function (key, value) {
            return ko.computed(function () {
                this.handling_caveats.valueHasMutated();
                return {"stix_value": ko.observable(key), "display_value": ko.observable(value)}
            }, this);
        },
        _parseResponse: function (configText) {
            if (configText !== null) {
                this.enabled(configText["enabled"] || false);
                this.savedEnabled(configText["enabled"] || false);

                ko.utils.objectForEach(configText["value"], function (key, value) {
                    this.saved_handling_caveats.push({
                         "stix_value" : key,
                        "display_value" : value
                    });
                    this.handling_caveats.push(this._createHandlingCaveat(key, value));

                }.bind(this));
            }
        },

        addGroup: function () {
            if (this.isHandlingCaveatsFull()) {
                this.handling_caveats().push(this._createHandlingCaveat("", ""));
                this.handling_caveats.valueHasMutated();
            }
        },

        isHandlingCaveatsFull: function () {
            var arrayLength = this.handling_caveats().length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.handling_caveats()[index]()['stix_value']() == "" || this.handling_caveats()[index]()['display_value']() == "") {
                    return false
                }
            }
            return true
        },

        save: function () {
            this.removeEmptyCaveats(this.handling_caveats());
            if (this.isValid(this.handling_caveats())) {
                var configObject = this.createSimpleConfigObject(this.handling_caveats());
                var successMessage = "The sharing group mappings were successfully saved";
                var errorMessage = "An error occurred while attempting to save the sharing groups configuration";
                this.saved_handling_caveats = [];
                for (var i in this.handling_caveats()) {
                    this.saved_handling_caveats.push({"stix_value": this.handling_caveats()[i]()["stix_value"](), "display_value": this.handling_caveats()[i]()["display_value"]()});
                }
                this.saveData("set_sharing_groups/", configObject, successMessage, errorMessage);
                this.something_to_save_trigger.valueHasMutated();
            } else {
                this.createErrorModal("All Handling Caveat mappings must be pairs of non-empty strings." +
                    " There must be no duplicate Stix or Display Values")
            }
        },

        removeEmptyCaveats: function (handlingCaveats) {
            var indexesToRemove = [];
            var arrayLength = handlingCaveats.length;
            for (var index = 0; index < arrayLength; index++) {
                if (handlingCaveats[index]()['stix_value']() == "" && handlingCaveats[index]()['display_value']() == "") {
                    //reverse order list of indices to remove
                    indexesToRemove.unshift(index)
                }
            }
            this.removeIndexes(indexesToRemove, handlingCaveats);
            this.handling_caveats.valueHasMutated();
            return handlingCaveats;
        },

        isValid: function (handlingCaveatArray) {
            if (this.containsDuplicates(this.handling_caveats())) {
                return false
            }
            var arrayLength = handlingCaveatArray.length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.isEmptyString(handlingCaveatArray[index]()['stix_value']()) == false ||
                    this.isEmptyString(handlingCaveatArray[index]()['display_value']()) == false)
                    return false
            }
            return true
        },

        containsDuplicates: function (handlingCaveats) {
            var stixValueArray = handlingCaveats.map(function (caveat) {
                return caveat().stix_value()
            });
            var displayValueArray = handlingCaveats.map(function (caveat) {
                return caveat().display_value()
            });

            return this.hasDuplicates(stixValueArray) || this.hasDuplicates(displayValueArray);
        },

        createSimpleConfigObject: function (handlingArray) {
            var markings = {};
            ko.utils.arrayForEach(handlingArray, function (arrayItem) {
                markings[arrayItem().stix_value()] = arrayItem().display_value()
            });

            return {
                "enabled": this.enabled(),
                "value": markings
            }
        }

    });
});
