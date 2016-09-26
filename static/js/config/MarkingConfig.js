define([
    "dcl/dcl",
    "knockout",
    "config/base-mongo-config"
], function (declare, ko, baseMongoConfig) {
    "use strict";

    var Marking = function (marking) {
        this.marking = ko.observable(marking);
    };

    return declare(baseMongoConfig, {
        declaredClass: "MarkingConfig",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "get_markings/", "An error occurred while attempting to retrieve the Marking Priorities.");
                this.marking_priorities = ko.observableArray([]);
                this.savedMarkingPriorities = ko.observableArray([]);
                this.markingsChanged = ko.computed(function () {
                    var bothMarkings = [];
                    ko.utils.arrayForEach(this.marking_priorities(), function (item) {
                        bothMarkings.push(item.marking())
                    });
                    ko.utils.arrayForEach(this.savedMarkingPriorities(), function (item) {
                        bothMarkings.push(item)
                    });
                    var distinctValues = ko.utils.arrayGetDistinctValues(bothMarkings).filter(function (item) { return item}); //remove empty items
                    return distinctValues.length != this.savedMarkingPriorities().length;
                }, this);

                this.enabled.subscribe(this._onEnabledChanged.bind(this));
                this.changesPending = ko.computed(this.changesPending, this);
            }
        }),

        _parseResponse: function (/*Array*/configText) {
            if (configText !== null) {
                this.enabled(configText["enabled"] || false);
                this.savedEnabled(configText["enabled"] || false);

                var mappedData = ko.utils.arrayMap(configText["value"], function (marking) {
                    return new Marking(marking)
                });
                this.marking_priorities(mappedData);

                ko.utils.arrayForEach(this.marking_priorities(), function (item) {
                    this.savedMarkingPriorities.push(item.marking());
                }.bind(this));
            }
        },

        save: function () {
            this.removeEmptyData();
            var successMessage = "The Marking Priorities were successfully saved";
            var errorMessage = "An error occurred while attempting to save the Marking Priorities configuration";
            this.saveData("set_markings/", this.parseMarkings(), successMessage, errorMessage);
        },

        changesPending: function () {
            return this.gotConfig() &&
                (
                    this.enabled() != this.savedEnabled() ||
                    this.markingsChanged()
                );
        },

        _onEnabledChanged: function () {
            if (!(this.enabled())) {
                this.marking_priorities.removeAll();
                ko.utils.arrayForEach(this.savedMarkingPriorities(), function (item) {
                    this.marking_priorities.push(new Marking(item))
                }.bind(this));
            }
        },

        _onSuccesfulSave: function (response, successMessage) {
            var modal = this.createSuccessModal(successMessage);

            this.savedMarkingPriorities.removeAll();
            ko.utils.arrayForEach(this.marking_priorities(), function (item) {
                this.savedMarkingPriorities.push(item.marking());
            }.bind(this));
            this.savedEnabled(this.enabled());

            modal.show();
        },

        removeEmptyData: function () {
            var indexesToRemove = [];
            var checkEmpty = this.isEmptyString;
            var arrayLength = this.marking_priorities().length;
            for (var index = 0; index < arrayLength; index++) {
                if (!checkEmpty(this.marking_priorities()[index].marking())) {
                    //reverse order list of indices to remove
                    indexesToRemove.unshift(index)
                }
            }
            this.removeIndexes(indexesToRemove, this.marking_priorities());
            this.marking_priorities.valueHasMutated();
        },

        parseMarkings: function () {
            var markingArray = [];
            ko.utils.arrayForEach(this.marking_priorities(), function (marking) {
                markingArray.push(marking.marking())
            });
            return {
                "enabled": this.enabled(),
                "value": markingArray
            }
        },

        addMarking: function () {
            if (this.markingIsFull()) {
                this.marking_priorities.push(new Marking(""));
            }
        },

        markingIsFull: function () {
            var arrayLength = this.marking_priorities().length;
            for (var index = 0; index < arrayLength; index++) {
                if (this.isEmptyString(this.marking_priorities()[index].marking()) == false)
                    return false
            }
            return true
        }
    });
});
