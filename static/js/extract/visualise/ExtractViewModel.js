define([
    "dcl/dcl",
    "knockout",
    "d3",
    "common/modal/Modal",
    "visualiser/ViewModel",
    "visualiser/panel-action/PanelActionsBuilder",
    "visualiser/panel-action/PanelAction",
    "kotemplate!modal-error-content:publisher/templates/error-modal-content.html"
], function (declare, ko, d3, Modal, ViewModel, PanelActionsBuilder, PanelAction, errorContentTemplate) {

    var base_url = "/adapter/certuk_mod/ajax/extract_visualiser/";

    var ExtractViewModel = declare(null, {
        declaredClass: "ExtractViewModel",
        constructor: function (rootIds) {
            this.viewModels = ko.observableArray([]);
            this.viewModelsById = {};

            this.viewModels.subscribe(function () {
                if (this.viewModels().length == rootIds.length) {
                    ko.applyBindings(
                        this,
                        document.getElementById('content')
                    );
                }
            }.bind(this))

            for (var i = 0; i < rootIds.length; i++) {
                this.initViewModel(rootIds[i])
            }
        },

        initViewModel: function (id) {
            ViewModel.loadById(
                id,
                base_url,
                base_url + "item/",
                (new PanelActionsBuilder())
                    .addAction(create_merge_action(id))
                    .addAction(create_delete_action(id))
                    .build(),

                function (viewModel) {
                    this.viewModelsById[viewModel.rootId()] = viewModel;
                    this.viewModels.push(viewModel);
                }.bind(this),

                function (error) {
                    showErrorModal(error.message)
                });
        },

        findByLabel: function (label) {
            return this.viewModelsById[label]
        }
    });

    function postAndReloadGraph(url, id, ids, graph) {
        postJSON(base_url + url, {
            'id': id,
            'ids': ids
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

                        graph.loadData(response);
                    }
                );
            }
        });
    }

    function showErrorModal(message) {
        (new Modal({
            title: "Error",
            titleIcon: "glyphicon-warning-sign",
            contentData: message,
            contentTemplate: errorContentTemplate.id,
            width: "90%"
        })).show();
    }

    function no(type) {
        return false;
    }

    function only_obs(type) {
        return type === "obs";
    }

    function create_delete_action(id) {
        return new PanelAction(
            only_obs,
            no,
            function (obs_ids_to_delete, graph) {
                postAndReloadGraph("delete_observables/", id, obs_ids_to_delete, graph);
            },
            "Delete",
            "trash");
    }

    function create_merge_action(id) {
        return new PanelAction(
            only_obs,
            no,
            function (obs_ids_to_merge, graph) {
                postAndReloadGraph("merge_observables/", id, obs_ids_to_merge, graph);
            },
            "Merge",
            "resize-small");
    }

    return ExtractViewModel;
});
