require([
    "knockout",
    "common/modal/Modal",
    "extract/upload/ExtractUploadModel",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (ko, Modal, ExtractUploadModel, errorContentTemplate) {
    try {
        ko.applyBindings(new ExtractUploadModel(), document.getElementById("content"));
    }
    catch (e) {
        var errorModal = new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: e.message,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        });

        errorModal.getButtonByLabel("OK").callback = history.back.bind(history);
        errorModal.show();
    }
});
