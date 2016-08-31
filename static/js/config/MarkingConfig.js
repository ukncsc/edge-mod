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
                sup.call(this);
                this.marking_priorities = ko.observableArray([]);
            }
        }),

        getConfig: function () {
            this.getData("get_markings/", "An error occurred while attempting to retrieve the Marking Priorities.");
        },

        _parseResponse: function (/*Array*/configText) {
            if (configText !== null) {
                this.enabled(configText["enabled"] || false);
                var mappedData = ko.utils.arrayMap(configText["value"], function (marking) {
                    return new Marking(marking)
                });
                this.marking_priorities(mappedData);
            }
        },

        save: function () {
            this.removeEmptyData();
            var successMessage = "The Marking Priorities were successfully saved";
            var errorMessage = "An error occurred while attempting to save the Marking Priorities configuration";
            this.saveData("set_markings/", this.parseMarkings(), successMessage, errorMessage);
        },

        removeEmptyData: function () {
            var indexesToRemove = [];
            var checkEmpty = this.isEmptyString
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
