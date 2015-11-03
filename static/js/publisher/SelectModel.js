define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "stix/StixPackage",
    "kotemplate!publish-modal:./templates/publish-modal-content.html"
], function (declare, ko, Modal, StixPackage, publishModalTemplate) {
    "use strict";

    return declare(null, {
        constructor: function (rootId, stixPackage, validationInfo) {
            this.stixPackage = ko.observable(new StixPackage(stixPackage, rootId, validationInfo));

            this.root = ko.computed(function () {
                return this.stixPackage().root;
            }, this);
            this.type = ko.computed(function () {
                return this.stixPackage().type;
            }, this);
        },

        _onPublishModalOK: function (modal) {
            var yesButton = modal.getButtonByLabel("Yes");
            var noButton = modal.getButtonByLabel("No");
            var closeButton = modal.getButtonByLabel("Close");

            yesButton.disabled(true);
            noButton.disabled(true);

            modal.contentData.waitingForResponse(true);
            modal.contentData.message("Publishing...");

            this.publish(function(response) {
                modal.contentData.waitingForResponse(false);

                var success = !!(response["success"]);
                var errorMessage = response["error_message"];
                if (errorMessage) {
                    errorMessage = errorMessage.replace(/^[A-Z]/, function(match) {
                        return match.toLowerCase();
                    }).replace(/[,.]+$/, "");
                }
                var message = success?
                    "The package was successfully published." :
                    "An error occurred during publish (" + errorMessage + "). Would you like to try again?";
                var title = success ? "Success" : "Error";
                var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";

                modal.title(title);
                modal.titleIcon(titleIcon);
                modal.contentData.message(message);

                if (success) {
                    yesButton.hide(true);
                    noButton.hide(true);
                    closeButton.hide(false);
                } else {
                    yesButton.disabled(false);
                    noButton.disabled(false);
                }
            }.bind(this));
        },

        onPublish: function () {
            var validations = this.stixPackage().validations();
            var contentData = {
                message: ko.observable("Are you absolutely sure you want to publish this package?"),
                messageWarning: "This package has warnings. If you wish to proceed, please describe below why you believe the warnings are not relevant in this case",
                messageError: "This package has errors and cannot be published",
                validations: validations,
                publicationMessage: ko.observable(""),
                waitingForResponse: ko.observable(false)
            };

            var hasErrors = validations.hasErrors();
            var confirmModal = new Modal({
                title: hasErrors ? "Error" : "Warning",
                titleIcon: hasErrors ? "glyphicon-ban-circle" : "glyphicon-exclamation-sign",
                contentData: contentData,
                contentTemplate: publishModalTemplate.id,
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        callback: this._onPublishModalOK.bind(this),
                        disabled: ko.observable(false),
                        icon: "glyphicon-ok",
                        hide: ko.observable(false)
                    },
                    {
                        label: "No",
                        icon: "glyphicon-remove",
                        disabled: ko.observable(false),
                        hide: ko.observable(false)
                    },
                    {
                        label: "Close",
                        hide: ko.observable(true)
                    }
                ]
            });

            if (hasErrors) {
                confirmModal.getButtonByLabel("Yes").hide(true);
                confirmModal.getButtonByLabel("No").hide(true);
                confirmModal.getButtonByLabel("Close").hide(false);
            } else if (validations.hasWarnings()) {
                var publicationMessage = contentData.publicationMessage;
                publicationMessage.subscribe(function (newValue) {
                    var hasMessage = (typeof newValue === "string" && newValue.length > 0);
                    confirmModal.getButtonByLabel("Yes").disabled(!hasMessage);
                });
                publicationMessage.valueHasMutated();
            }
            confirmModal.show();
        },

        publish: function(onPublishCallback) {
            postJSON("/adapter/publisher/ajax/publish/", {
                root_id: this.root().id()
            }, onPublishCallback);
        },

        onRowClicked: function (item) {
            var path = window.location.href.split("/");
            path[path.length - 1] = item.id();
            window.location.assign(path.join("/"));
        }
    });
});
