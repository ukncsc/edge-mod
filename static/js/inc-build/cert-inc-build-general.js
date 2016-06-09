define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-messages",
    "common/cert-identity",
    "common/topic",
    "inc-build/cert-inc-build-topics",
    "text!config-service"
], function (declare, ko, AbstractBuilderForm, Messages, CERTIdentity, Topic, topics, configService) {
    "use strict";

    var config = Object.freeze(JSON.parse(configService));
    var sharing_groups = config.sharing_groups;

    return declare(AbstractBuilderForm, {
        declaredClass: "General",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "General");

                this.title = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to enter a title for your indicator"
                    }
                });
                this.shortDescription = ko.observable();
                this.description = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to enter a description for your indicator"
                    }
                });
                this.confidence = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a confidence level for your indicator"
                    }
                });
                this.status = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a status for your indicator"
                    }
                });
                this.tlp = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a TLP for your indicator"
                    }
                });

                this.reporter = ko.observable(null);
                this.reporter.extend({
                    requiredGroupedCustom: {
                        required: true,
                        group: this.validationGroup,
                        validateFunction: function () {
                            return this.reporter();
                        }.bind(this),
                        displayMessage: "You need to select a reporter for your indicator"
                    }
                });

                this.markings = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a marking for your indicator"
                    }
                });

                this.handling_caveat = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a handling caveat for your indicator"
                    }
                });

                this.handling_caveats = ko.observableArray([]);
                this.statuses = ko.observableArray([]);
                this.marking_priorities = ko.observableArray([]);
                this.confidences = ko.observableArray([]);
                this.categories = ko.observableArray();
                this.tlps = ko.observableArray([]);
            }
        }),

        loadStatic: function (optionLists) {
            this.confidences(optionLists.confidence_list);
            this.tlps(optionLists.tlps_list);
            this.statuses(optionLists.statuses_list);
            this.categories(optionLists.categories_list);
            this.marking_priorities(optionLists.marking_priorities);
            this.handling_caveats(this.generateCaveatLabelArray(sharing_groups));
        },

        generateCaveatLabelArray: function (sharingGroups) {
            var LabelList = []
            for (var key in sharingGroups) {
                if (sharingGroups.hasOwnProperty(key)) {
                    LabelList.push(sharingGroups[key])
                }
            }
            return LabelList
        },

        findValueOfCaveat: function (sharingGroups, label) {
            for (var key in sharingGroups) {
                if (sharingGroups.hasOwnProperty(key)) {
                    if (sharingGroups[key] == label) {
                        return key
                    }
                }
            }
        },

        getLabelForCaveat: function (sharingGroups, value) {
            for (var key in sharingGroups) {
                if (sharingGroups.hasOwnProperty(key)) {
                    if (key == value) {
                        return sharingGroups[key]
                    }
                }
            }
        },

        addReporter: function () {
            var newIdentity = new CERTIdentity();
            newIdentity.ModelUI().done(function () {
                this.reporter(newIdentity);
            }.bind(this));
        },

        load: function (data) {
            this.title(data["title"] || "");
            this.status(data["status"] || "");
            this.shortDescription(data["short_description"] || "");
            this.description(data["description"] || "");
            if ('reporter' in data) {
                if ('identity' in data['reporter']) {
                    this.reporter(new CERTIdentity().load(data["reporter"]["identity"]))
                }
            }

            this.confidence(data["confidence"] || "");
            this.tlp(data["tlp"] || "");

            if ("markings" in data && data["markings"].length == 0) {
                this.markings("");
            } else {
                this.markings(data["markings"] || "");
            }

            if ("handling_caveat" in data && data["handling_caveat"].length == 0) {
                this.handling_caveat("");
            } else {
                this.handling_caveat(this.getLabelForCaveat(sharing_groups, data["handling_caveat"]) || "");
            }

            this.status.subscribe(function (data) {
                Topic.publish(topics.STATUS_CHANGE, data);
            }.bind(this));
        },

        save: function () {
            return {
                title: this.title(),
                status: this.status(),
                short_description: this.shortDescription(),
                description: this.description(),
                confidence: this.confidence(),
                reporter: {'identity': this.reporter().to_json()},
                tlp: this.tlp(),
                markings: this.markings(),
                handling_caveat: this.findValueOfCaveat(sharing_groups, this.handling_caveat())
            };
        }
    });

});
