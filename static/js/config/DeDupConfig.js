define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "config/base-config"
], function (declare, ko, Modal, BaseConfig) {
    "use strict";

    //var type_labels = Object.freeze({
    //    "ind": "Indicator",
    //    "obs": "Observable",
    //    "ttp": "TTP",
    //    "coa": "Course Of Action",
    //    "act": "Threat Actor",
    //    "cam": "Campaign",
    //    "inc": "Incident",
    //    "tgt": "Exploit Target",
    //    "pkg": "Package"
    //});

    return declare(BaseConfig, {
        declaredClass: "DeDupConfig",
        constructor: declare.superCall(function (sup) {
            return function () {
                sup.call(this, 'Online DeDup', 'dedup_task', 'dedup_config');

                this.localNamespaceOnly = ko.observable();
                this.savedLocalNamespaceOnly = ko.observable();
                this.objectTypes = ko.observableArray();
                this.savedObjectTypes = ko.observableArray();

                this.enabled.subscribe(this._onEnabledChanged.bind(this));
                this.changesPending = ko.computed(this.changesPending, this);
            }
        }),

        _parseConfigResponse: declare.superCall(function (sup) {
            return function (response) {
                // Would make sense here to use the KO Mapping plugin to allow easy conversion from JSON...
                this.localNamespaceOnly(response["localNamespaceOnly"]);
                this.savedLocalNamespaceOnly(response["localNamespaceOnly"]);

                sup.call(this, response);
            }
        }),

        _onEnabledChanged: function () {
            if (!(this.enabled())) {
                this.localNamespaceOnly(this.savedLocalNamespaceOnly());
                this.time(this.savedTime());
            }
        },

        changesPending: function () {
            return this.gotConfig() &&
                (
                    this.localNamespaceOnly() != this.savedLocalNamespaceOnly() ||
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

                var postUrl = reset ? "../ajax/reset_dedup_config/" : "../ajax/set_dedup_config/";
                var postData = reset ? {} : {
                    localNamespaceOnly: this.localNamespaceOnly(),
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

                    this.savedLocalNamespaceOnly(this.localNamespaceOnly());
                    this.savedTime(this.time());
                    this.savedEnabled(this.enabled());
                }
            }
        })
    });
});
