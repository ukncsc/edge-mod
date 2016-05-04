define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "config/base-config"
], function (declare, ko, Modal, BaseConfig) {
    "use strict";

    return declare(BaseConfig, {
        declaredClass: "RetentionConfig",

        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, "FTS rebuild", "fts_task", "fts_config");

                this.fullBuild = ko.observable();
                this.savedFullBuild = ko.observable();
                this.enabled.subscribe(this._onEnabledChanged.bind(this));

                this.changesPending = ko.computed(this.changesPending, this);
            }
        }),

        _parseConfigResponse: declare.superCall(function (sup) {
            return function (response) {
                // Would make sense here to use the KO Mapping plugin to allow easy conversion from JSON...
                this.fullBuild(response["fullBuild"]);
                this.savedFullBuild(response["fullBuild"]);

                sup.call(this, response);
            }
        }),

        _onEnabledChanged: function () {
            if (!(this.enabled())) {
                this.fullBuild(this.savedFullBuild());
                this.time(this.savedTime());
            }
        },

        changesPending: function () {
            return this.gotConfig() &&
                (
                    this.fullBuild() != this.savedFullBuild() ||
                    this.time() != this.savedTime() ||
                    this.enabled() != this.savedEnabled()
                );
        },

        _basicValidate: function () {
            var errors = [];
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

                var postUrl = reset ? "../ajax/reset_fts_config/" : "../ajax/set_fts_config/";
                var postData = reset ? {} : {
                    fullBuild: this.fullBuild(),
                    time: this.time(),
                    enabled: this.enabled()
                };

                postJSON(postUrl, postData, function (response) {
                    this._processSaveResponse(modal, reset, response);
                }.bind(this));
            }
        },

        _processSaveResponse: declare.superCall(function (sup) {
            return function (modal, reset, response) {
                sup.call(this, modal, reset, response);

                var success = !!(response["success"]);

                if (success) {
                    if (reset) {
                        this._parseConfigResponse(response);
                    }

                    this.savedFullBuild(this.fullBuild());
                    this.savedTime(this.time());
                    this.savedEnabled(this.enabled());
                }
            }
        })
    });
});
