define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-messages",
    "common/cert-identity"
], function (declare, ko, AbstractBuilderForm, Messages, CERTIdentity) {
    "use strict";

    var General = declare(AbstractBuilderForm, {
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

                this.reporter = ko.observable(new CERTIdentity());
                this.reporter().UUID.extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a reporter for your indicator"
                    }
                })

                this.markings = ko.observable().extend({
                    requiredGrouped: {
                        required: true,
                        group: this.validationGroup,
                        displayMessage: "You need to select a marking for your indicator"
                    }
                });

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
        },

        generalShowModal: function () {
            return this.reporter().ModelUI()
        },

        load: function (data) {
            this.title(data["title"] || "");
            this.status(data["status"] || "");
            this.shortDescription(data["shortDescription"] || "");
            this.description(data["description"] || "");
            if ('reporter' in data) {
                if ('identity' in data['reporter']) {
                    if ('UUID' in data['reporter']['identity'])
                        this.reporter(new CERTIdentity().load(data['reporter']['identity']))
                }
            }


            this.confidence(data["confidence"] || "");
            this.tlp(data["tlp"] || "");
            if ("markings" in data && data["markings"].length == 0) {
                this.markings("");
            } else {
                this.markings(data["markings"] || "");
            }
        },


        save: function () {
            return {
                title: this.title(),
                status: this.status(),
                shortDescription: this.shortDescription(),
                description: this.description(),
                confidence: this.confidence(),
                reporter: {'identity': this.reporter().to_json()},
                tlp: this.tlp(),
                markings: this.markings()
            };
        }
    });

    return General;
});
