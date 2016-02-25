define([
    "dcl/dcl",
    "ind-build/indicator-builder-shim",
    "knockout",
    "common/modal/Modal",
    "kotemplate!builder-publish:./templates/builder-publish-modal.html",
    "stix/ValidationInfo",
    "kotemplate!validation-results:../publisher/templates/validation-results.html"
], function (declare, indicator_builder, ko, Modal, builderPublishModalTemplate, ValidationInfo) {
    "use strict";

    function buildRestUrl(/*String*/ path) {
        return indicator_builder["ajax_uri"] + path + "/";
    }

    function PublishModalContent () {
        this.message = ko.observable("");
        this.status = ko.observable("OK");
        this.validations = null;
        this.waitingForResponse = ko.observable(false);
        this.clientErrors = ko.observableArray([]);
        this.responseType = ko.observable(null);
        this.statusMessage = ko.computed(function () {
            return this.messagesByStatus[this.status()];
        }, this);
        this.hasErrors = ko.computed(function () {
            return this.status() === "FAILED" || this.status() === "ERROR";
        }, this);
        this.hasWarnings = ko.computed(function () {
            return this.status() === "WARNING";
        }, this);
        this.hasInfos = ko.computed(function () {
            return this.status() === "INFO";
        }, this);
    }
    PublishModalContent.prototype.messagesByStatus = {
        "FAILED": "Unable to publish this indicator",
        "ERROR": "This indicator has errors and cannot be published",
        "WARNING": "This indicator has warnings",
        "INFO": "",
        "OK": ""
    };

    var CERTViewModel = declare(indicator_builder.viewModel, {
        declaredClass: "CERTViewModel",
        messageConfirmPublish: "Are you sure you want to publish?",
        REDIRECT_DELAY: 2000,

        publish: function () {
            var contentData = this._constructPublishModalContent();
            var clientValidation = this.section().doValidation();
            var hasErrors = clientValidation.hasErrors();
            var confirmModal = new Modal({
                title: hasErrors ? "Unable to publish" : "Publish",
                titleIcon: hasErrors ? "glyphicon-ban-circle" : "glyphicon-exclamation-sign",
                contentData: contentData,
                contentTemplate: builderPublishModalTemplate.id,
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        callback: this._publish.bind(this),
                        icon: "glyphicon-ok",
                        hide: ko.observable(true),
                        disabled: ko.observable(false)
                    },
                    {
                        label: "No",
                        icon: "glyphicon-remove",
                        hide: ko.observable(true),
                        disabled: ko.observable(false)
                    },
                    {
                        label: "Close",
                        hide: ko.observable(false),
                        disabled: ko.observable(false)
                    }
                ]
            });

            confirmModal.show();

            if (hasErrors) {
                contentData.responseType("CLIENT_ERROR");
                contentData.status("ERROR");
                contentData.message("");
                contentData.clientErrors(clientValidation.errors.peek());
            } else {
                this._validate.call(this, confirmModal);
            }
        },

        _constructPublishModalContent: function () {
            return new PublishModalContent();
        },

        _serializeIndicator: function () {
            var data = this.section().save();
            data.id = this.id();
            data.id_ns = this.id_ns();
            data.composition_type = this.compositionType();
            data.stixtype = 'ind';
            return data;
        },

        _validate: function (modal) {
            modal.contentData.waitingForResponse(true);
            modal.contentData.message("Validating...");
            modal.getButtonByLabel("Close").disabled(true);

            var data = this._serializeIndicator();

            this.getValidationResult(data, function (response) {
                var rawValidation = response['validation_info'];
                var validations = new ValidationInfo(rawValidation);
                modal.contentData.message("");
                modal.contentData.validations = validations;

                modal.contentData.waitingForResponse(false);
                modal.contentData.responseType("VAL");

                if (!response["success"]) {
                    modal.title("Error");
                    modal.titleIcon("glyphicon-exclamation-sign");
                    modal.contentData.status("FAILED");
                    modal.contentData.message("An error occurred during validation (" + response["error_message"] + ")");
                    modal.getButtonByLabel("Close").disabled(false);
                    return;
                }

                if (validations.hasErrors()) {
                    modal.title("Error");
                    modal.titleIcon("glyphicon-exclamation-sign");
                    modal.contentData.status("ERROR");
                    modal.getButtonByLabel("Close").disabled(false);
                } else if (validations.hasWarnings() || validations.hasInfos()) {
                    modal.getButtonByLabel("Yes").hide(false);
                    modal.getButtonByLabel("No").hide(false);
                    modal.getButtonByLabel("Close").hide(true);
                    modal.contentData.message(this.messageConfirmPublish);
                    if (validations.hasWarnings()) {
                        modal.contentData.status("WARNING");
                    } else {
                        modal.contentData.status("INFO");
                    }
                } else {
                    modal.contentData.status("OK");
                    modal.contentData.message("Validation successful...");
                    setTimeout(function () {
                        this._publish(modal);
                    }.bind(this), this.REDIRECT_DELAY);
                }
            }.bind(this));
        },

        getValidationResult: function (data, onResponseCallback) {
            postJSON("/adapter/certuk_mod/ajax/validate/", data, onResponseCallback);
        },

        _publish: function (modal) {
            modal.contentData.message("Publishing...");
            modal.contentData.waitingForResponse(true);
            modal.contentData.responseType(null);
            modal.getButtonByLabel("Yes").disabled(true);
            modal.getButtonByLabel("No").disabled(true);
            modal.getButtonByLabel("Close").disabled(true);

            this.getPublishResult(this._serializeIndicator(), function (response) {
                modal.contentData.waitingForResponse(false);
                modal.contentData.responseType("PUB");

                modal.getButtonByLabel("Yes").hide(true);
                modal.getButtonByLabel("No").hide(true);
                modal.getButtonByLabel("Close").disabled(false);
                modal.getButtonByLabel("Close").hide(false);

                if (response["success"]) {
                    modal.contentData.status("OK");
                    modal.contentData.message("The indicator has been published internally");
                    modal.titleIcon("glyphicon-ok-sign");

                    window.location.assign('/object/' + this.id());

                    setTimeout(function () {
                        window.location.assign(window.location.href.split("/indicator/")[0] + "/indicator/build/");
                    }, this.REDIRECT_DELAY);
                } else {
                    modal.contentData.status("FAILED");
                    modal.contentData.message(response["message"]);
                    modal.titleIcon("glyphicon-exclamation-sign");
                }
            }.bind(this));
        },

        getPublishResult: function (data, onResponseCallback) {
            postJSON(buildRestUrl("create_indicator"), data, onResponseCallback);
        },

        saveDraft: function () {
            var title = ko.unwrap(this.section().findByLabel("General")).title;
            if (title.hasError()) {
                alert("You need to enter a title for your indicator");
            } else {
                var data = this._serializeIndicator();
                postJSON(buildRestUrl("save_draft"), data, function (response) {
                    if (response["success"]) {
                        this.tracker().markCurrentStateAsClean();
                    } else {
                        alert(response["message"]);
                    }
                }.bind(this));
            }
        }
    });

    indicator_builder.viewModel = CERTViewModel;
    return CERTViewModel;
});
