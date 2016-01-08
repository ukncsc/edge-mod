require([
    "knockout",
    "common/modal/Modal",
    "dedup/DuplicateModel",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (ko, Modal, DuplicateModel, errorContentTemplate) {
    try {
        var duplicateModel = new DuplicateModel();
        ko.applyBindings(duplicateModel, document.getElementById("content"));
        duplicateModel.loadDuplicates();
    } catch (e) {
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
