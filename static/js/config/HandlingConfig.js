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
                this.savedHandlingCaveats = ko.observableArray([]);
                this.handlingCaveatsChanged = ko.computed(function () {
                    return true;
                }, this);

                this.enabled.subscribe(this._onEnabledChanged.bind(this));
                this.changesPending = ko.computed(this.changesPending, this);
            }
        }),

        _parseResponse: function (configText) {
            if (configText !== null) {
                this.enabled(configText["enabled"] || false);
                this.savedEnabled(configText["enabled"] || false);

                ko.utils.objectForEach(configText["value"], function (key, value) {
                    this.handling_caveats.push(ko.observable({
                        "stix_value": key,
                        "display_value": value
                    }))
                }.bind(this));

                this.savedHandlingCaveats(this.handling_caveats());
            }
        },

        addGroup: function () {
            if (this.isHandlingCaveatsFull()) {
                this.handling_caveats().push({"stix_value": "", "display_value": ""});
                this.handling_caveats.valueHasMutated();
            }
        },

        isHandlingCaveatsFull: function () {
            var arrayLength = this.handling_caveats().length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.handling_caveats()[index]['stix_value'] == "" || this.handling_caveats()[index]['display_value'] == "") {
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
                this.saveData("set_sharing_groups/", configObject, successMessage, errorMessage);
            } else {
                this.createErrorModal("All Handling Caveat mappings must be pairs of non-empty strings." +
                    " There must be no duplicate Stix or Display Values")
            }
        },

        removeEmptyCaveats: function (handlingCaveats) {
            var indexesToRemove = [];
            var arrayLength = handlingCaveats.length;
            for (var index = 0; index < arrayLength; index++) {
                if (handlingCaveats[index]['stix_value'] == "" && handlingCaveats[index]['display_value'] == "") {
                    //reverse order list of indices to remove
                    indexesToRemove.unshift(index)
                }
            }
            this.removeIndexes(indexesToRemove, handlingCaveats);
            this.handling_caveats.valueHasMutated();
        },

        isValid: function (handlingCaveatArray) {
            if (this.containsDuplicates(this.handling_caveats())) {
                return false
            }
            var arrayLength = handlingCaveatArray.length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.isEmptyString(handlingCaveatArray[index]['stix_value']) == false ||
                    this.isEmptyString(handlingCaveatArray[index]['display_value']) == false)
                    return false
            }
            return true
        },

        changesPending: function () {
            return this.gotConfig() &&
                (
                    this.enabled() != this.savedEnabled() ||
                    this.handlingCaveatsChanged()
                );
        },

        _onEnabledChanged: function () {
            if(!this.enabled()) {
                this.handling_caveats.removeAll();
                ko.utils.arrayForEach(this.savedHandlingCaveats(), function (item) {
                    this.handling_caveats.push({"stix_value": item.stix_value, "display_value": item.display_value})
                }.bind(this));
            }
        },

        _onSuccesfulSave: function (response, successMessage) {
            var modal = this.createSuccessModal(successMessage);

            this.savedHandlingCaveats.removeAll();
            ko.utils.arrayForEach(this.marking_priorities(), function (item) {
                this.savedMarkingPriorities.push(item.marking());
            }.bind(this));
            this.savedEnabled(this.enabled());

            modal.show();
        },

        containsDuplicates: function (handlingCaveats) {
            var stixValueArray = handlingCaveats.map(function (caveat) {
                return caveat.stix_value
            });
            var displayValueArray = handlingCaveats.map(function (caveat) {
                return caveat.display_value
            });

            if (this.hasDuplicates(stixValueArray) || this.hasDuplicates(displayValueArray)) {
                return true
            }
        },

        createSimpleConfigObject: function (handlingArray) {
            var markings = {};
            ko.utils.arrayForEach(handlingArray, function (arrayItem) {
                markings[arrayItem.stix_value] = arrayItem.display_value
            });

            return {
                "enabled": this.enabled(),
                "value": markings
            }
        }

    });
});
