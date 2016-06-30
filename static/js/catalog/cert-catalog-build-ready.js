require([
    "knockout",
    "common/modal/show-error-modal",
    "catalog/cert-catalog-view-model",
    "domReady!"
], function (ko, showErrorModal, SelectModel) {

    var viewModel = new SelectModel(window["rootId"], window["stixPackage"], window["validationInfo"], window["viewURL"], window["editURL"], window["revisions"]);

    viewModel.loadStatic({
        "revisions": window["revisions"]
    });

    ko.applyBindings(viewModel);


});
