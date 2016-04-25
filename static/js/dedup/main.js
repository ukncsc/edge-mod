require([
    "knockout",
    "common/modal/show-error-modal",
    "dedup/DuplicateModel",
    "domReady!"
], function (ko, showErrorModal, DuplicateModel) {
    try {
        var duplicateModel = new DuplicateModel();
        ko.applyBindings(duplicateModel, document.getElementById("content"));
        duplicateModel.loadDuplicates();
    } catch (e) {
        showErrorModal(e.message, true);
    }
});
