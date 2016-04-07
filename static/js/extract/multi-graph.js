require([
    "dcl/dcl",
    "knockout",
    "d3",
    "common/modal/Modal",
    "visualiser/ViewModel",
    "visualiser/PanelActions",
    "visualiser/PanelActionsBuilder",
    "visualiser/PanelAction",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html",
    "domReady!"
], function (declare, ko, d3, Modal, ViewModel, PanelActions, PanelActionsBuilder, PanelAction, errorContentTemplate) {
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
            var base_url = "/adapter/certuk_mod/ajax/extract_visualiser/"
            ViewModel.loadById(id,
                base_url,
                base_url + "item/",
                (new PanelActionsBuilder()).
                    addAction(create_merge_action(base_url, id)).
                    addAction(create_delete_action(base_url, id)).
                    build(),

                function (viewModel) {
                    this.viewModelsById[viewModel.rootId()] = viewModel;
                    this.viewModels.push(viewModel);
                }.bind(this));
        },

        findByLabel: function (label) {
            return this.viewModelsById[label]
        }
    });

    function create_delete_action(base_url, id) {
        return new PanelAction(
            function (type) {
                return type === "obs";
            },

            function (type) {
                return false;
            },

            function (obs_ids_to_delete, graph) {


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

                postJSON(base_url + "delete_observables/", {
                    'id': id,
                    'ids': obs_ids_to_delete
                }, function (result) {
                    if ('message' in result) {
                        showErrorModal(result['message'])
                    } else {
                        d3.json(
                            base_url + encodeURIComponent(id),
                            function (error, response) {
                                if (error) {
                                    showErrorModal(error);
                                }

                                //location.reload();
                                graph.loadData(response);
                            }
                        );
                    }
                });

            },
        "delete",
        "trash");
    }

    function create_merge_action(base_url, id) {
        return new PanelAction(
            function (type) {
                return type === "obs";
            },

            function (type) {
                return false;
            },

            function (obs_ids_to_merge, graph) {

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

                postJSON(base_url + "merge_observables/", {
                    'id': id,
                    'ids': obs_ids_to_merge
                }, function (result) {
                    if ('message' in result) {
                        showErrorModal(result['message'])
                    } else {
                        d3.json(
                            base_url + encodeURIComponent(id),
                            function (error, response) {
                                if (error) {
                                    showErrorModal(error);
                                }

                                //location.reload();
                                graph.loadData(response);
                            }
                        );
                    }
                });

            },
        "merge",
        "resize-small");
    }

    return new MultiGraph(window['root_ids']);
});
