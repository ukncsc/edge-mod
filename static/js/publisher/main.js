require([
    "knockout",
    "common/modal/Modal",
    "publisher/SelectModel",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (ko, Modal, SelectModel, errorContentTemplate) {
    try {
        ko.applyBindings(
            new SelectModel(window["rootId"], window["stixPackage"], window["validationInfo"]),
            document.getElementById("content")
        );
    } catch (e) {
        console.error(e);
/*
        var errorModal = new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: e.message,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        });
        errorModal.getButtonByLabel("OK").callback = history.back.bind(history);
        errorModal.show();
*/
    }
});
