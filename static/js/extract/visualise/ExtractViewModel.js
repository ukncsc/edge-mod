define([
    "dcl/dcl",
    "knockout",
    "d3",
    "common/modal/ShowErrorModal",
    "visualiser/ViewModel",
    "visualiser/panel-action/PanelActionsBuilder",
    "visualiser/panel-action/PanelAction"
], function (declare, ko, d3, ShowErrorModal, ViewModel, PanelActionsBuilder, PanelAction) {

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
        _postJSON(base_url + url, { // Calling _ version as error callback required
                'id': id,
                'ids': ids
            }, function (result) {
                d3.json(
                    base_url + encodeURIComponent(id),
                    function (error, response) {
                        if (error) {
                            showErrorModal(error);
                        }

                        graph.loadData(response);
                    }
                );
            },
            function (result) {
                showErrorModal(JSON.parse(result.responseText)['Error'])
            }
        );
    }

    function showErrorModal(message) {
         ShowErrorModal(message, false);
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
