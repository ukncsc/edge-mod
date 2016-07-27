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
            var mappedData = ko.utils.arrayMap(configText, function (marking) {
                return new Marking(marking)
            });
            this.marking_priorities(mappedData);
        },

        save: function () {
            var successMessage = "The Marking Priorities were successfully saved";
            var errorMessage = "An error occurred while attempting to save the Marking Priorities configuration";
            this.saveData("set_markings/", this.parseMarkings(), successMessage, errorMessage);
        },

        parseMarkings: function () {
            var markingArray = [];
            ko.utils.arrayForEach(this.marking_priorities(), function (marking) {
                markingArray.push(marking.marking())
            });
            return markingArray
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
