define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-messages",
    "common/identity",
    "common/topic",
    "inc-build/cert-inc-build-topics",
    "text!config-service"
], function (declare, ko, AbstractBuilderForm, Messages, Identity, Topic, topics, configService) {
    "use strict";

    var markingsEnabled = false;

    var config = Object.freeze(JSON.parse(configService));
    var markingsConfig = config.markings;

    if (markingsConfig) {
        var markings = markingsConfig.markings;
        markingsEnabled = markingsConfig.enabled
    }

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
                this.markingsEnabled = ko.observable(markingsEnabled);
                if (markingsEnabled) {
                    this.markings = ko.observable().extend({
                        requiredGrouped: {
                            required: true,
                            group: this.validationGroup,
                            displayMessage: "You need to select a marking for your indicator"
                        }
                    });
                }
                this.statuses = ko.observableArray([]);
                if (markingsEnabled) {
                    this.marking_priorities = ko.observableArray([]);
                }
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
            if (markingsEnabled) {
                this.marking_priorities(markings);
            }
        },

        addReporter: function () {
            if (this.reporter() == null) {
                var newIdentity = new Identity();
                newIdentity.ModelUI().done(function () {
                    this.reporter(newIdentity);
                }.bind(this));
            } else {
                this.reporter().ModelUI().done();
            }
        },

        load: function (data) {
            this.title(data["title"] || "");
            this.status(data["status"] || "");
            this.shortDescription(data["short_description"] || "");
            this.description(data["description"] || "");
            if ('reporter' in data) {
                if ('identity' in data['reporter']) {
                    this.reporter(new Identity().load(data["reporter"]["identity"]))
                }
            }

            this.confidence(data["confidence"] || "");
            this.tlp(data["tlp"] || "");

            if (this.markingsEnabled()) {
                if ("markings" in data && data["markings"].length == 0) {
                    this.markings("");
                } else {
                    this.markings(data["markings"] || "");
                }
            }
            this.status.subscribe(function (data) {
                Topic.publish(topics.STATUS_CHANGE, data);
            }.bind(this));
        },

        save: function () {
            if (this.markingsEnabled()) {
                return this.incidentWithMarking();
            } else {
                return this.incidentWithoutMarking();
            }
        },

        incidentWithMarking: function () {
            return {
                title: this.title(),
                status: this.status(),
                short_description: this.shortDescription(),
                description: this.description(),
                confidence: this.confidence(),
                reporter: {'identity': this.reporter().to_json()},
                tlp: this.tlp(),
                markings: this.markings()
            };
        },

        incidentWithoutMarking: function () {
            return {
                title: this.title(),
                status: this.status(),
                short_description: this.shortDescription(),
                description: this.description(),
                confidence: this.confidence(),
                reporter: {'identity': this.reporter().to_json()},
                tlp: this.tlp()
            };
        }
    });

});
