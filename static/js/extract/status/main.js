require([
    "knockout",
    "common/modal/show-error-modal",
    "extract/status/ExtractStatusModel",
    "domReady!"
], function (ko, showErrorModal, ExtractStatusModel) {
    try {
        ko.applyBindings(new ExtractStatusModel(), document.getElementById("content"));
    }
    catch (e) {
        showErrorModal(e.message, true);
    }
});
