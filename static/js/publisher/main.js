require([
    "knockout",
    "common/modal/show-error-modal",
    "publisher/SelectModel",
    "domReady!"
], function (ko, showErrorModal, SelectModel) {
    try {
        ko.applyBindings(
            new SelectModel(window["rootId"], window["stixPackage"], window["validationInfo"], window["viewURL"], window["editURL"]),
            document.getElementById("content")
        );
    } catch (e) {
        showErrorModal(e.message, true);
    }
});
