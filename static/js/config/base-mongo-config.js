define([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "common/modal/show-error-modal"
], function (declare, ko, Modal, showErrorModal) {

    return declare(null, {
        declaredClass: "base-mongo-config",
        constructor: function () {
            this.enabled = ko.observable(false);
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
            //stub - does nothing here
        },

        isValid: function (data) {
            //stub - does nothing here
        },

        hasDuplicates: function (array) {
            return (new Set(array)).size !== array.length;
        },

        removeIndexes: function (toRemove, arrayToPurge) {
            var numberToRemove = toRemove.length;
            for (var index = 0; index < numberToRemove; index++) {
                //works back through array so safely remove, no falling off
                arrayToPurge.splice(toRemove[index], 1)
            }
        },

        isEmptyString: function (/*String*/ string) {
            return typeof string === "string" && string.trim().length > 0;
        },

        saveData: function (/*String*/ url, data, /*String*/ successMessage, /*String*/ errorMessage) {
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
