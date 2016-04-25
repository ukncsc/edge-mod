require([
    "knockout",
    "common/modal/ShowErrorModal",
    "visualiser/ViewModel",
    "visualiser/panel-action/PanelActionsBuilder",
    "domReady!"
], function (ko, ShowErrorModal, ViewModel, PanelActionsBuilder) {
    ViewModel.loadById(
        window["rootId"],
        "/adapter/certuk_mod/ajax/visualiser/",
        "/adapter/certuk_mod/ajax/visualiser/item/",
        (new PanelActionsBuilder()).build(),
        function (viewModel) {
            ko.applyBindings(
                viewModel,
                document.getElementById("content")
            );
        }, function (e) {
            ShowErrorModal(e.message, true);
        });
});
