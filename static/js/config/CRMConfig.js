define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!pub-config-modal:./templates/config-modal-content.html"
], function (declare, ko, Modal, publishModalTemplate) {

    return declare(null, {
        declaredClass: "CRMConfig",
        constructor: function () {
            this.CRMURL = ko.observable();
        },

        getURL: function () {
            getJSON("get_crm_url", {}, function (response) {
                this._parseResponse(response);
            }.bind(this), function (error) {
                this.createErrorModal("An error occurred while attempting to retrieve the CRM configuration.");
            }.bind(this));
        },

        _parseResponse: function (response) {
            this.CRMURL(response["crmURL"]);
        },

        createErrorModal: function (content) {
            var errorModal = new Modal({
                title: "Error",
                titleIcon: "glyphicon-exclamation-sign",
                contentData: content
            });
            errorModal.show();
        },

        onSave: function () {
            if (this.isValid(this.CRMURL())) {
                this.saveURL(this.CRMURL());
            } else {
                this.createErrorModal("The CRM url must be a valid url ending with /crmapi");
            }
        },

        isValid: function (url) {
            var endsWithCRM = /crmapi$/;
            return endsWithCRM.test(url)
        },

        saveURL: function (url) {
            postJSON("set_crm_url/", url, function (response) {
                this._onSuccesfulSave(response);
            }.bind(this), function (error) {
                this.createErrorModal("An error occurred while attempting to save the CRM configuration (" + error + ").")
            }.bind(this));
        },

        _onSuccesfulSave: function (modal, response) {
            var modal = new Modal({
                title: "Success",
                titleIcon: "glyphicon-ok-sign",
                contentData: "The CRM settings were saved successfully."
            });
            modal.show();
        }
    });

});
