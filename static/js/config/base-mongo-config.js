define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "common/modal/show-error-modal"
], function (declare, ko, Modal, showErrorModal) {

    return declare(null, {
        declaredClass: "base-mongo-config",
        constructor: function () {
        },

        getData: function (url, errorMessage) {
            getJSON(url, {}, function (response) {
                this._parseResponse(response);
            }.bind(this), function (error) {
                this.createErrorModal(errorMessage + " (" + error + ").")
            }.bind(this));
        },

        //abstract
        _parseResponse: function (response) {
            //stub - does nothing here
        },


        createErrorModal: function (content) {
            showErrorModal(content, false);
        },

        //abstract
        save: function () {
            //stub
        },

        saveData: function (/*String*/ url, data,/*String*/ successMessage, /*String*/ errorMessage) {
            postJSON(url, data, function (response) {
                this._onSuccesfulSave(response, successMessage);
            }.bind(this), function (error) {
                this.createErrorModal(errorMessage + " (" + error + ").")
            }.bind(this));
        },

        _onSuccesfulSave: function (response, successMessage) {
            var modal = this.createSuccessModal(successMessage)
            modal.show();
        },

        createSuccessModal: function (content) {
            return new Modal({
                title: "Success",
                titleIcon: "glyphicon-ok-sign",
                contentData: content
            });
        }
    });

});
