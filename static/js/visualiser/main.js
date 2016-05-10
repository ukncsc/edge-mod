require([
    "knockout",
    "common/modal/show-error-modal",
    "visualiser/ViewModel",
    "visualiser/panel-action/PanelActionsBuilder",
    "domReady!"
], function (ko, showErrorModal, ViewModel, PanelActionsBuilder) {
    ViewModel.loadById(
        window["rootId"],
        "/adapter/certuk_mod/ajax/visualiser/",
        "/adapter/certuk_mod/ajax/visualiser/item/",
        "/adapter/certuk_mod/review/",
        "visualiser-graph",
        (new PanelActionsBuilder()).build(),
        function (viewModel) {
            ko.applyBindings(
                viewModel,
                document.getElementById("content")
            );
        }, function (e) {
            showErrorModal(e.message, true);
        });
});
