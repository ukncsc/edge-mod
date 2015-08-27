define([
    "dcl/dcl",
    "knockout",
    "common/modal/ConfirmModal",
    "common/modal/Modal",
    "stix/StixPackage",
    "kotemplate!publish-modal:common/modal/publish-modal-content.html"
], function (declare, ko, ConfirmModal, Modal, StixPackage, publishTemplate) {
    "use strict";

    return declare(null, {
        constructor: function (rootId, stixPackage) {
            this.stixPackage = ko.observable(new StixPackage(stixPackage, rootId));

            this.root = ko.computed(function () {
                return this.stixPackage().root;
            }, this);
            this.type = ko.computed(function () {
                return this.stixPackage().type;
            }, this);
        },

        onPublish: function () {
            var contentData = {
                message: ko.observable("Are you absolutely sure you want to publish this package?"),
                waitingForResponse: ko.observable(false)
            };

            var onOKCallback = function(modal) {
                var yesButton = modal.getButtonByLabel("Yes");
                var noButton = modal.getButtonByLabel("No");
                var closeButton = modal.getButtonByLabel("Close");

                yesButton.disabled(true);
                noButton.disabled(true);

                contentData.waitingForResponse(true);

                this.publish(function(response) {
                    contentData.waitingForResponse(false);

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

                    testConfirmModal.title(title);
                    testConfirmModal.titleIcon(titleIcon);
                    contentData.message(message);

                    if (success) {
                        yesButton.hide(true);
                        noButton.hide(true);
                        closeButton.hide(false);
                    } else {
                        yesButton.disabled(false);
                        noButton.disabled(false);
                    }
                }.bind(this));
            }.bind(this);

            var testConfirmModal = new Modal({
                title: "Warning",
                titleIcon: "glyphicon-exclamation-sign",
                contentData: contentData,
                contentTemplate: publishTemplate.id,
                buttonData: [
                    {
                        label: "Yes",
                        noClose: true,
                        callback: onOKCallback,
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

            testConfirmModal.show();
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
