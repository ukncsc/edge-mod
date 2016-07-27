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
            if (this.isValid(this.marking_priorities())) {
                var successMessage = "The Marking Priorities were successfully saved";
                var errorMessage = "An error occurred while attempting to save the Marking Priorities configuration";
                this.saveData("set_markings/", this.parseMarkings(), successMessage, errorMessage);
            } else {
                this.createErrorModal("All Markings must be non-empty unique strings.")
            }
        },

        parseMarkings: function () {
            var markingArray = [];
            ko.utils.arrayForEach(this.marking_priorities(), function (marking) {
                markingArray.push(marking.marking())
            });
            return markingArray
        },

        isValid: function (markings) {
            return true;
        },

        addMarking: function () {
            if (this.markingIsFull()) {
                this.marking_priorities.push(new Marking(""));
            }
        },

        markingIsFull: function () {
           /* ko.utils.arrayForEach(this.marking_priorities(), function (marking){
                if(this.isEmptyString("")){
                    return false
                }
            });              */
            return true
        }
    });
});
