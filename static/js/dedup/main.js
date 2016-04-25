require([
    "knockout",
    "common/modal/ShowErrorModal",
    "dedup/DuplicateModel",
    "domReady!"
], function (ko, ShowErrorModal, DuplicateModel) {
    try {
        var duplicateModel = new DuplicateModel();
        ko.applyBindings(duplicateModel, document.getElementById("content"));
        duplicateModel.loadDuplicates();
    } catch (e) {
        ShowErrorModal(e.message, true);
    }
});
