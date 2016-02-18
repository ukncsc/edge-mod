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

        constructor: declare.superCall(function(sup) {
            return function () {
                sup.call(this, "General");

                this.title = ko.observable().extend({required: true});
                this.short_description = ko.observable();
                this.description = ko.observable();
                this.confidence = ko.observable().extend({required: true});
                this.status = ko.observable();
                this.category = ko.observable();
                this.tlp = ko.observable();
                this.reporter = ko.observable();
                this.reporter(new CERTIdentity({name: 'Click to edit'}))
                this.markings = ko.observable();
                this.statuses = ko.observableArray([]);
                this.confidences = ko.observableArray([]);
                this.categories = ko.observableArray();
                this.tlps = ko.observableArray([]);
            }
        }),

        loadStatic : function (optionLists) {
            this.confidences(optionLists.confidence_list);
            this.tlps(optionLists.tlps_list);
            this.statuses(optionLists.statuses_list);
            this.categories(optionLists.categories_list);
        },

        generalShowModal : function (namearg) {
            return (new CERTIdentity()).ModelUI(namearg)
        },

        load : function (data) {
            this.title(data["title"] || "");
            this.status(data["status"] || "");
            this.category(data["category"] || "");
            this.short_description(data["short_description"] || "");
            this.description(data["description"] || "");
            if ('reporter' in data) {
                if ('identity' in data['reporter']) {
                    if ('name' in data['reporter']['identity'])
                        this.reporter((new CERTIdentity()).ModelUI(data['reporter']['identity']))
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

        doValidation : function () {
            var msgs = new Messages();
            if (!this.title()) {
                msgs.addError("You need to enter a title for your incident");
            }
            if (!this.confidence()) {
                msgs.addError("You need to enter a confidence for your incident");
            }
            return msgs;
        },

        save : function () {
            return {
                title: this.title(),
                status: this.status(),
                category: this.category(),
                short_description: this.short_description(),
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
