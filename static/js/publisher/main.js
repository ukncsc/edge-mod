require([
    "knockout",
    "common/modal/Modal",
    "publisher/SelectModel",
    "common/ValidationStatus",
    "domReady!"
], function (ko, Modal, SelectModel, ValidationStatus) {
    try {
        window.ValidationStatus = ValidationStatus;
        ko.applyBindings(
            new SelectModel(rootId, stixPackage, validationInfo),
            document.getElementById("content")
        );
    } catch (e) {
        var errorModal = new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: e.message
        });
        errorModal.getButtonByLabel("OK").callback = history.back.bind(history);
        errorModal.show();
    }
});
