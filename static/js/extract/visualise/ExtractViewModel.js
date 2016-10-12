define([
    "dcl/dcl",
    "knockout",
    "d3",
    "common/modal/show-error-modal",
    "common/topic",
    "visualiser/ViewModel",
    "visualiser/panel-action/PanelActionsBuilder",
    "visualiser/panel-action/PanelAction",
    "visualiser/graph/topics"
], function (declare, ko, d3, showErrorModal, topic, ViewModel, PanelActionsBuilder, PanelAction, topics) {
    var base_url = "/adapter/certuk_mod/ajax/extract_visualiser/";

    var ExtractViewModel = declare(null, {
        declaredClass: "ExtractViewModel",
        constructor: function (rootIds, indicatorInformation) {
            this.viewModels = ko.observableArray([]);
            this.viewModelsById = {};
            this.failedIds = ko.observableArray([]);
            this.indicatorInformationTypeById = {};

            this.viewModels.subscribe(function () {
                if (this.viewModels().length + this.failedIds().length == rootIds.length) {
                    ko.applyBindings(
                        this,
                        document.getElementById('content')
                    );
                    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
                        topic.publish(topics.RESIZE, e.target.id);
                    });

                    $(".nav-tabs").bind("DOMNodeInserted", function () {   //When a new tab is added, reset
                        $('a[data-toggle="tab"]').off('shown.bs.tab');

                        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
                            topic.publish(topics.RESIZE, e.target.id);
                        });
                    });
                }
            }.bind(this));

            for (var i = 0; i < rootIds.length; i++) {
                this.indicatorInformationTypeById[rootIds[i]] = indicatorInformation[i];
                this.initViewModel(rootIds[i])
            }
        },

        initViewModel: function (id) {
            ViewModel.loadById(
                id,
                base_url,
                base_url + "item/",
                "/object/",

                (new PanelActionsBuilder())
                    .addAction(create_merge_action(id))
                    .addAction(create_delete_action(id))
                    .addAction(create_move_action(id, this))
                    .build(),

                function (viewModel) {
                    this.viewModelsById[viewModel.rootId()] = viewModel;
                    this.viewModels.push(viewModel);
                }.bind(this),

                function (error) {
                    this.failedIds.push(id);
                }.bind(this));
        },

        findByLabel: function (label) {
            return this.viewModelsById[label]
        },
        findTypeByLabel: function (label) {
            return this.indicatorInformationTypeById[label].type_name;
        },
        findSafeTypeByLabel: function (label) {
            return this.indicatorInformationTypeById[label].safe_type_name;
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
                            showErrorModal(error, false);
                        }

                        graph.loadData(response);
                    }
                );
            },
            function (result) {
                showErrorModal(JSON.parse(result.responseText)['Error'], false)
            }
        );
    }

    function postAndAddNewIndicator(url, id, ids, graph, vm) {
        _postJSON(base_url + url, { // Calling _ version as error callback required
                'id': id,
                'ids': ids
            }, function (result) {
                d3.json(
                    base_url + encodeURIComponent(id),
                    function (error, response) {
                        if (error) {
                            showErrorModal(error, false);
                        }

                        new_indicator = result.new_indicator;
                        vm.indicatorInformationTypeById[new_indicator['id']] = new_indicator;
                        vm.initViewModel(new_indicator['id']);
                        graph.loadData(response);
                    }
                );
            },
            function (result) {
                showErrorModal(JSON.parse(result.responseText)['Error'], false)
            }
        );
    }
    //NOTE: this function is sometimes give two arguments and this must be handled
    function only_obs(type, rel_type) {
        return type === "obs";
    }

    function create_delete_action(id) {
        return new PanelAction(
            only_obs,
            function (obs_ids_to_delete, graph) {
                postAndReloadGraph("delete_observables/", id, obs_ids_to_delete, graph);
            },
            "Delete",
            "trash");
    }

    function create_move_action(id, vm) {
        return new PanelAction(
            only_obs,
            function (obs_ids_to_move, graph) {
                postAndAddNewIndicator("move_observables/", id, obs_ids_to_move, graph, vm);
            },
            "Move",
            "share-alt");
    }

    function create_merge_action(id) {
        return new PanelAction(
            only_obs,
            function (obs_ids_to_merge, graph) {
                postAndReloadGraph("merge_observables/", id, obs_ids_to_merge, graph);
            },
            "Merge",
            "resize-small");
    }

    return ExtractViewModel;
});
