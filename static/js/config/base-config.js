define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!ret-config-modal:./templates/config-modal-content.html"
], function (declare, ko, Modal, configModalTemplate) {
    "use strict";

    return declare(null, {
        declaredClass: "BaseConfig",
        constructor: function (configType, endPointTask, endPointConfig) {
            this.endPointTask = ko.observable(endPointTask);
            this.endPointConfig = ko.observable(endPointConfig);
            this.configType = ko.observable(configType);

            this.time = ko.observable();
            this.enabled = ko.observable();
            this.savedEnabled = ko.observable();
            this.gotConfig = ko.observable(false);
            this.savedTime = ko.observable();

            this.running = ko.observable();
            this.getTaskStatus();
        },

        getTaskStatus: function () {
            postJSON("../ajax/get_" + this.endPointTask() + "_status/", {}, function (response) {
                this.running(!!response['status']);
                setTimeout(this.getTaskStatus.bind(this), 10000);
            }.bind(this));
        },

        runNow: function () {
            if (!this.running() && !this.changesPending()) {
                postJSON("../ajax/run_" + this.endPointTask() + "/", {}, function (response) {
                    var modal = new Modal({
                        title: this.configType(),
                        titleIcon: "glyphicon-info-sign",
                        contentData: "The " + this.configType() + " job has been scheduled to run (celery task ID '" + response['id'] + "')."
                    });
                    modal.show();
                }.bind(this));
            }
        },

        _parseConfigResponse: function (response) {
            // Would make sense here to use the KO Mapping plugin to allow easy conversion from JSON...
            this.time(response["time"]);
            this.savedTime(response["time"]);

            this.enabled(response["enabled"]);
            this.savedEnabled(response["enabled"]);
        },

        getConfig: function () {
            this.gotConfig(false);
            postJSON("../ajax/get_" + this.endPointConfig() + "/", {}, function (response) {
                this.gotConfig(true);
                if (response["success"]) {
                    this._parseConfigResponse(response);
                } else {
                    var errorModal = new Modal({
                        title: "Error",
                        titleIcon: "glyphicon-exclamation-sign",
                        contentData: "An error occurred while attempting to retrieve the " + this.configType() + " configuration."
                    }.bind(this));
                    errorModal.show();
                }
            }.bind(this));
        },

        _processSaveResponse: function (modal, reset, response) {
            modal.contentData.waitingForResponse(false);
            modal.getButtonByLabel("Close").disabled(false);

            var success = !!(response["success"]);

            var title = success ? "Success" : "Error";
            var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";
            var message = success ? "The " + this.configType() + " settings were saved successfully." :
            "An error occurred while attempting to save (" + response["error_message"] + ").";

            modal.contentData.message(message);
            modal.title(title);
            modal.titleIcon(titleIcon);
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
