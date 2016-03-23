require([
    "dcl/dcl",
    "knockout",
    "common/modal/Modal",
    "visualiser/ViewModel",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (declare, ko, Modal, ViewModel, errorContentTemplate) {
    var MultiGraph = declare(null, {
        declaredClass: "Modal",
        constructor: function (rootIds) {
            this.viewModels = ko.observableArray([])
            this.viewModelsById = {};

            for (var i = 0; i < rootIds.length; i++) {
                ViewModel.loadById(rootIds[i], function (viewModel) {
                    this.viewModelsById[viewModel.rootId()] = viewModel;
                    this.viewModels.push(viewModel);
                }.bind(this));
            }

            this.viewModels.subscribe(function () {

                if (this.viewModels().length == rootIds.length) {
                    ko.applyBindings(
                        this,
                        document.getElementById('content')
                    );
                }
            }.bind(this))
        },

        findByLabel : function(label) {
            return this.viewModelsById[label]
        }
    });

    return new MultiGraph(window['ids_only']);
});
