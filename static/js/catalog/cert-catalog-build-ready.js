require([
    "knockout",
    "common/modal/show-error-modal",
    "catalog/cert-catalog-view-model",
    "domReady!"
], function (ko, showErrorModal, SelectModel) {
    try {
        ko.applyBindings(
            new SelectModel(window["rootId"], window["stixPackage"], window["validationInfo"], window["viewURL"], window["editURL"], window["revisions"]),
            document.getElementById("content")
        );
    } catch (e) {
        showErrorModal(e.message, true);
    }
});
