require([
    "dcl/dcl",
    "knockout",
    "d3",
    "common/modal/Modal",
    "visualiser/ViewModel",
    "visualiser/PanelActions",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (declare, ko, d3, Modal, ViewModel, PanelActions, errorContentTemplate) {
    var MultiGraph = declare(null, {
        declaredClass: "Modal",
        constructor: function (rootIds) {
            this.viewModels = ko.observableArray([])
            this.viewModelsById = {};

            for (var i = 0; i < rootIds.length; i++) {
                this.initViewModel(rootIds[i])
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


        initViewModel: function (id) {
            ViewModel.loadById(id,
                "/adapter/certuk_mod/ajax/extract_visualiser/",
                "/adapter/certuk_mod/ajax/extract_visualiser/item/",
                new PanelActions(function (type) {
                        return type === "obs";
                    }, function (type) {
                        return false;
                    }, function () {
                        var list_obs_ids_to_merge = []
                        ko.utils.arrayForEach(this.graph().nodes(), function (node) {
                            if (node.isChecked()) {
                                list_obs_ids_to_merge.push(node.id());
                            }
                        })

                        function showErrorModal(message) {
                            var errorModal = new Modal({
                                title: "Error",
                                titleIcon: "glyphicon-warning-sign",
                                contentData: message,
                                contentTemplate: errorContentTemplate.id,
                                width: "90%"
                            });
                            errorModal.show();
                        }

                        postJSON("/adapter/certuk_mod/ajax/extract_visualiser/merge_observables/", {
                            'id': this.selectedObject()._rootId._id,
                            'ids': list_obs_ids_to_merge
                        }, function (result) {
                            if ('message' in result) {
                                showErrorModal(result['message'])
                            } else {
                                d3.json(
                                    "/adapter/certuk_mod/ajax/extract_visualiser/" + encodeURIComponent(id),
                                    function (error, response) {
                                        if (error) {
                                            showErrorModal(error);
                                        }

                                        this.updateGraphData(response);
                                    }.bind(this)
                                );
                            }
                        }.bind(this));

                    },
                    "merge"),

                function (viewModel) {
                    this.viewModelsById[viewModel.rootId()] = viewModel;
                    this.viewModels.push(viewModel);
                }.bind(this));
        },

        findByLabel: function (label) {
            return this.viewModelsById[label]
        }
    });

    return new MultiGraph(window['root_ids']);
});
