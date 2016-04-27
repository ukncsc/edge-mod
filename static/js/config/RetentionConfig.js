define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "config/base-config"
], function (declare, ko, Modal, BaseConfig) {
    "use strict";

    function inputIsInteger (value) {
        return isFinite(value) && Math.floor(value) == value;
    }

    return declare(BaseConfig, {
        declaredClass: "RetentionConfig",
        constructor: declare.superCall(function(sup) {
            return function(){
            sup.call(this, "Retention", "purge_task", "retention_config")

            this.age = ko.observable();
            this.sightings = ko.observable();
            this.backLinks = ko.observable();
            this.enabled = ko.observable();

            this.savedAge = ko.observable();
            this.savedSightings = ko.observable();
            this.savedBackLinks = ko.observable();
            this.savedEnabled = ko.observable();


            this.changesPending = ko.computed(this.changesPending, this);
        }}),

        _parseConfigResponse: declare.superCall(function(sup) {
            return function (response) {
                // Would make sense here to use the KO Mapping plugin to allow easy conversion from JSON...
                this.age(response["max_age_in_months"]);
                this.savedAge(response["max_age_in_months"]);

                this.sightings(response["minimum_sightings"]);
                this.savedSightings(response["minimum_sightings"]);

                this.backLinks(response["minimum_back_links"]);
                this.savedBackLinks(response["minimum_back_links"]);

                sup.call(this, response)
            }
            }),

        _onEnabledChanged: function () {
            if (!(this.enabled())) {
                this.age(this.savedAge());
                this.sightings(this.savedSightings());
                this.backLinks(this.savedBackLinks());
                this.time(this.savedTime());
            }
        },

        changesPending: function () {
            return this.gotConfig() &&
                (
                    this.age() != this.savedAge() ||
                    this.sightings() != this.savedSightings() ||
                    this.backLinks() != this.savedBackLinks() ||
                    this.time() != this.savedTime() ||
                    this.enabled() != this.savedEnabled()
                );
        },

        _basicValidate: function () {
            var errors = [];

            if (!inputIsInteger(this.age())) {
                errors.push("The maximum age must be an integer.");
            } else if (this.age() < 1) {
                errors.push("The maximum age must be greater than zero.");
            }

            if (!inputIsInteger(this.sightings())) {
                errors.push("The minimum sightings must be an integer.");
            } else if (this.sightings() < 2) {
                errors.push("The minimum sightings must be greater than one.");
            }

            if (!inputIsInteger(this.backLinks())) {
                errors.push("The minimum back links must be an integer.");
            } else if (this.backLinks() < 1) {
                errors.push("The minimum back links must be greater than zero.");
            }

            if (!this.time()) {
                errors.push("A time must be configured.")
            }

            return errors;
        },

        _save: function (modal, reset) {
            var errors = [];
            if (!reset) {
                errors = this._basicValidate();
            }

            var modalContent = modal.contentData;
            if (errors.length > 0) {
                modalContent.waitingForResponse(false);
                modalContent.message(errors.join(" "));
                modal.title("Error");
                modal.titleIcon("glyphicon-exclamation-sign");
            } else {
                modalContent.waitingForResponse(true);
                modalContent.message("Saving...");
                modal.getButtonByLabel("Close").disabled(true);

                var postUrl = reset ? "../ajax/reset_retention_config/" : "../ajax/set_retention_config/";
                var postData = reset ? { } : {
                    max_age_in_months: Number(this.age()),
                    minimum_sightings: Number(this.sightings()),
                    minimum_back_links: Number(this.backLinks()),
                    time: this.time(),
                    enabled: this.enabled()
                };

                postJSON(postUrl, postData, function (response) {
                    this._processSaveResponse(modal, reset, response);
                }.bind(this));
            }
        },

        _processSaveResponse: declare.superCall(function(sup) {
            return function (modal, reset, response) {
                sup.call(this, modal, reset, response);

                var success = !!(response["success"]);

                if (success) {
                    if (reset) {
                        this._parseConfigResponse(response);
                    }

                    this.savedAge(this.age());
                    this.savedSightings(this.sightings());
                    this.savedBackLinks(this.backLinks());
                    this.savedTime(this.time());
                    this.savedEnabled(this.enabled());
                }

            }
        })
    });
});
