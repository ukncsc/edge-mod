require([
    "knockout",
    "common/modal/Modal",
    "publisher/SelectModel",
    "domReady!"
], function (ko, Modal, SelectModel) {
    try {
        ko.applyBindings(
            new SelectModel(rootId, stixPackage),
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
