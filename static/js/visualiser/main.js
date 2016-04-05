require([
    "knockout",
    "common/modal/Modal",
    "visualiser/ViewModel",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (ko, Modal, ViewModel, errorContentTemplate) {
    try {

        ViewModel.loadById(
            window["rootId"],
            "/adapter/certuk_mod/ajax/visualiser/",
            "/adapter/certuk_mod/ajax/visualiser/item/",
            function (viewModel) {
                ko.applyBindings(
                    viewModel,
                    document.getElementById("content")
                );
            });
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
