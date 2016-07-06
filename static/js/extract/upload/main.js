require([
    "knockout",
    "common/modal/show-error-modal",
    "extract/upload/ExtractUploadModel",
    "domReady!"
], function (ko, showErrorModal, ExtractUploadModel) {
    try {
        ko.applyBindings(new ExtractUploadModel(), document.getElementById("content"));
    }
    catch (e) {
        showErrorModal(e.message, true);
    }
});
