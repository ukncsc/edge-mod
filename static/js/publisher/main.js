require([
    "knockout",
    "common/modal/ShowErrorModal",
    "publisher/SelectModel",
    "domReady!"
], function (ko, ShowErrorModal, SelectModel) {
    try {
        ko.applyBindings(
            new SelectModel(window["rootId"], window["stixPackage"], window["validationInfo"]),
            document.getElementById("content")
        );
    } catch (e) {
        ShowErrorModal(e.message, true);
    }
});
