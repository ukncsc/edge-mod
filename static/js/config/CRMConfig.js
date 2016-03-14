define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "kotemplate!pub-config-modal:./templates/config-modal-content.html"
], function (declare, ko, Modal, publishModalTemplate) {

    return declare(null, {
        declaredClass: "CRMConfig.js",
        constructor: function () {
            this.CRMURL = ko.observable();
        },

        getURL: function () {
            getJSON("get_crm_url", {}, function (response) {
                //should do valid check against http code, not looking for success in object
                if (response["success"]) {
                    this._parseResponse(response);
                } else {
                    var errorModal = new Modal({
                        title: "Error",
                        titleIcon: "glyphicon-exclamation-sign",
                        contentData: "An error occurred while attempting to retrieve the CRM configuration."
                    });
                    errorModal.show();
                }
            }.bind(this));
        },

        _parseResponse: function (response) {
            this.CRMURL(response["crm-url"]);
        },

        onSave: function () {
            if (this.isValid(this.CRMURL())) {
                this.saveURL(this.CRMURL());
            } else {
                var errorModal = new Modal({
                    title: "Error",
                    titleIcon: "glyphicon-exclamation-sign",
                    contentData: "This must be a valid url ending in /crm-api"
                });
                errorModal.show();
            }
        },

        isValid: function (url) {
            //var isURL = /^(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?$/i;
            var endsWithCRM = /crm-api$/;

            return true//endsWithCRM.test(url)
        },

        saveURL: function (url) {
            var request = {
                "crm-url": url
            };

            postJSON("set_crm_url/", request, function (response) {
                this._processSaveResponse(modal, response);
            }.bind(this));
        },

        _processSaveResponse: function (modal, response) {
            modal.contentData.waitingForResponse(false);
            modal.getButtonByLabel("Close").disabled(false);

            var success = !!(response["success"]);

            var title = success ? "Success" : "Error";
            var titleIcon = success ? "glyphicon-ok-sign" : "glyphicon-exclamation-sign";
            var message = success ? "The retention settings were saved successfully." :
            "An error occurred while attempting to save (" + response["error_message"] + ").";

            modal.contentData.message(message);
            modal.title(title);
            modal.titleIcon(titleIcon);

            //not sure if need to reload but meh
            this._parseResponse(response);
        }
    });

});
