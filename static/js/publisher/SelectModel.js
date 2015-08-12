define([
    "dcl/dcl",
    "knockout",
    "common/modal/ConfirmModal",
    "common/modal/Modal",
    "stix/StixPackage"
], function (declare, ko, ConfirmModal, Modal, StixPackage) {
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
            var confirmModal = new ConfirmModal({
                title: "Warning",
                titleIcon: "glyphicon-exclamation-sign",
                contentData: "Are you absolutely sure you want to publish this package?",
                showIcons: true,
                onConfirm: this.publish.bind(this)
            });
            confirmModal.show();
        },

        publish: function() {
            postJSON("/adapter/publisher/ajax/publish/", {
                root_id: this.root().id()
            }, this._onPublishResponseReceived.bind(this));
        },

        _onPublishResponseReceived: function (response) {
            var message = response["success"] ? "The package was successfully published." : response["error_message"];
            var title = response["success"] ? "Success" : "Error";
            var modal = new Modal({
                title: title,
                contentData: message
            });
            modal.show();
        }
    });
});
