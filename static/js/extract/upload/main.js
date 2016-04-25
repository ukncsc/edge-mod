require([
    "knockout",
    "common/modal/ShowErrorModal",
    "extract/upload/ExtractUploadModel",
    "domReady!"
], function (ko, ShowErrorModal, ExtractUploadModel, errorContentTemplate) {
    try {
        ko.applyBindings(new ExtractUploadModel(), document.getElementById("content"));
    }
    catch (e) {
        ShowErrorModal(e.message, true);
    }
});
