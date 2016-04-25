define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "common/modal/ShowErrorModal",
    "kotemplate!ret-config-modal:./templates/config-modal-content.html"
], function (declare, ko, Modal, ShowErrorModal, configModalTemplate) {
    "use strict";

    function inputIsInteger(value) {
        return isFinite(value) && Math.floor(value) == value;
    }

    return declare(null, {
        declaredClass: "RetentionConfig",
        constructor: function () {
            this.time = ko.observable();
            this.enabled = ko.observable();
            this.fullBuild = ko.observable();
            this.enabled.subscribe(this._onEnabledChanged.bind(this));


            this.savedTime = ko.observable();
            this.savedFullBuild = ko.observable();
            this.savedEnabled = ko.observable();

            this.gotConfig = ko.observable(false);

            this.changesPending = ko.computed(this.changesPending, this);

            this.running = ko.observable();
            this.getTaskStatus();
        },

        getTaskStatus: function () {
            postJSON("../ajax/get_fts_task_status/", {}, function (response) {
                this.running(!!response['status']);
                setTimeout(this.getTaskStatus.bind(this), 10000);
            }.bind(this));
        },

        runNow: function () {
            if (!this.running() && !this.changesPending()) {
                postJSON("../ajax/run_fts_task/", {}, function (response) {
                    (new Modal({
                        title: "FTS rebuild",
                        titleIcon: "glyphicon-info-sign",
                        contentData: "The FTS rebuild job has been scheduled to run (celery task ID '" + response['id'] + "')."
                    })).show();
                });
            }
        },

        _parseConfigResponse: function (response) {
            // Would make sense here to use the KO Mapping plugin to allow easy conversion from JSON...
            this.time(response["time"]);
            this.savedTime(response["time"]);

            this.fullBuild(response["fullBuild"]);
            this.savedFullBuild(response["fullBuild"]);

            this.enabled(response["enabled"]);
            this.savedEnabled(response["enabled"]);
        },

        getConfig: function () {
            this.gotConfig(false);
            postJSON("../ajax/get_fts_config/", {}, function (response) {
                this.gotConfig(true);
                if (response["success"]) {
                    this._parseConfigResponse(response);
                } else {
                    ShowErrorModal("An error occurred while attempting to retrieve the retention configuration.", false);
                }
            }.bind(this));
        },

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

        _processSaveResponse: function (modal, reset, response) {
            modal.contentData.waitingForResponse(false);
            modal.getButtonByLabel("Close").disabled(false);

            var success = !!(response["success"]);

            var title = success ? "Success" : "Error";
            var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";
            var message = success ? "The fts rebuild settings were saved successfully." :
            "An error occurred while attempting to save (" + response["error_message"] + ").";

            modal.contentData.message(message);
            modal.title(title);
            modal.titleIcon(titleIcon);

            if (success) {
                if (reset) {
                    this._parseConfigResponse(response);
                }

                this.savedFullBuild(this.fullBuild());
                this.savedTime(this.time());
                this.savedEnabled(this.enabled());
            }
        },

        onSave: function (reset) {
            var contentData = {
                message: ko.observable(""),
                waitingForResponse: ko.observable(false)
            };

            var onSaveModal = new Modal({
                title: "Save settings",
                titleIcon: "glyphicon-cloud-upload",
                contentData: contentData,
                contentTemplate: configModalTemplate.id,
                onShow: function (modal) {
                    this._save.call(this, modal, reset);
                }.bind(this),
                buttonData: [
                    {
                        label: "Close",
                        hide: ko.observable(false),
                        disabled: ko.observable(false)
                    }
                ]
            });

            onSaveModal.show();
        }
    });
});
