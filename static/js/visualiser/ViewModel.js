define([
    "dcl/dcl",
    "knockout",
    "d3",
    "./graph/Graph",
    "../stix/StixPackage",
    "./toPNG/PNGConverter",
    "./graph/forceGraphBinding",
    "common/modal/show-error-modal",
    "common/modal/ConfirmModal"
], function (declare, ko, d3, Graph, StixPackage, PNGConverter, forceGraph, showErrorModal, ConfirmModal) {
    "use strict";

    var ViewModel = declare(null, {
        declaredClass: "ViewModel",

        constructor: function (rootId, graphData, graph_url, item_url, publish_url, panel_actions) {

            this.rootId = ko.computed(function () {
                return rootId;
            });

            this.graph_url = ko.computed(function () {
                return graph_url;
            });

            this.publish_url = ko.computed(function () {
                return publish_url;
            });

            this.panel_actions = ko.computed(function () {
                return panel_actions;
            });

            this.item_url = ko.computed(function () {
                return item_url;
            });
            this.graph = ko.observable(new Graph(graphData));
            this.graph().selectedNode.subscribe(this.onSelectedNodeChanged.bind(this));
            this.selectedObject = ko.observable(null);
            this.selectedRoot = ko.computed(function () {
                var root = null;
                var selectedObject = this.selectedObject();
                if (selectedObject) {
                    root = selectedObject.root;
                }
                return root;
            }, this);
            setTimeout(function () {
                this.graph().selectNode(rootId);
            }.bind(this), 100);

            this.backlinks = ko.observableArray([]);
            this.matches = ko.observableArray([]);
            this.no_edges = ko.observableArray([]);
            this.edges = ko.observableArray([]);
        },
        onNodeClicked: function (data) {
            if (data.nodeType() === 'external_ref') {
                return;
            }
            this.graph().selectNode(data.id());
        },
        onExternalPublish: function (data, scope) {
            window.open(this.publish_url() + encodeURIComponent(data));
        },
        onNewRootId: function (data, scope) {
            this.getExtended(
                data, [], [], [], [],
                function (result) {
                    this.rootId = ko.computed(function () {
                        return data;
                    });

                    this.graph().loadData(result);
                    this.backlinks.removeAll();
                    this.matches.removeAll();
                    this.edges.removeAll();
                    this.no_edges.removeAll();
                }.bind(this));
        },
        onPlusBacklinkClicked: function (data, scope) {
            this.getExtended(
                this.rootId(),
                this.backlinks().concat([data]),
                this.matches(),
                this.no_edges(),
                this.edges(),
                function (result) {
                    this.graph().loadData(result);
                    this.backlinks.push(data);
                    this.graph().findNode(data).isBackLinkShown(true);
                }.bind(this));
        },
        onMinusBacklinkClicked: function (data, scope) {
            var dataIndex = this.backlinks().indexOf(data);
            this.getExtended(
                this.rootId(),
                this.backlinks().slice().splice(dataIndex, dataIndex == -1 ? 0 : 1),
                this.matches(),
                this.no_edges(),
                this.edges(),
                function (result) {
                    this.graph().loadData(result);
                    this.backlinks.remove(data);
                    this.graph().findNode(data).isBackLinkShown(false);
                }.bind(this));
        },
        onShowEdges: function (data, scope) {
            var dataIndex = this.no_edges().indexOf(data);
            this.getExtended(
                this.rootId(),
                this.backlinks(),
                this.matches(),
                this.no_edges().slice().splice(dataIndex, dataIndex == -1 ? 0 : 1),
                this.edges().concat([data]),
                function (result) {
                    this.graph().loadData(result);
                    this.no_edges.remove(data);
                    this.edges.push(data);
                    this.graph().findNode(data).isEdgesShown(true);
                }.bind(this));
        },
        onHideEdges: function (data, scope) {
            var dataIndex = this.edges().indexOf(data);
            this.getExtended(
                this.rootId(),
                this.backlinks(),
                this.matches(),
                this.no_edges().concat([data]),
                this.edges().slice().splice(dataIndex, dataIndex == -1 ? 0 : 1),
                function (result) {
                    this.graph().loadData(result);
                    this.no_edges.push(data);
                    this.edges.remove(data);
                    this.graph().findNode(data).isEdgesShown(false);
                }.bind(this));
        },
        onPlusMatchesClicked: function (data, scope) {
            this.getExtended(
                this.rootId(),
                this.backlinks(),
                this.matches().concat([data]),
                this.no_edges(),
                this.edges(), function (result) {
                    this.graph().loadData(result);
                    this.matches.push(data);
                    this.graph().findNode(data).isMatchesShown(true);
                }.bind(this));
        },
        onMinusMatchesClicked: function (data, scope) {
            var dataIndex = this.matches().indexOf(data);
            this.getExtended(
                this.rootId(),
                this.backlinks(),
                this.matches().slice().splice(dataIndex, dataIndex == -1 ? 0 : 1),
                this.no_edges(),
                this.edges(), function (result) {
                    this.graph().loadData(result);
                    this.matches.remove(data);
                    this.graph().findNode(data).isMatchesShown(false);
                }.bind(this));
        },
        getExtended: function (rootId, bls, matches, no_edges, edges, successcb) {
            postJSON(this.graph_url() + "get_extended/", {
                    'id': rootId,
                    'id_bls': bls,
                    'id_matches': matches,
                    'hide_edge_ids': no_edges,
                    'show_edge_ids': edges
                }, function (result) {
                    var additionalNodes = result.nodes.length - this.graph().nodes().length
                    if (additionalNodes > 500) {
                        var options = {};
                        options['title'] = "Do you definitely want to show this data?";
                        options["isYesNo"] = true;
                        options['contentData'] = "An additional " +
                            additionalNodes +
                            " nodes has been requested, showing a large number of nodes may cause performance problems in your browser.";

                        var modal = new ConfirmModal(options);
                        modal.getButtonByLabel("Yes").callback = function () {
                            successcb(result)
                        };
                        modal.show();
                    } else {
                        successcb(result);
                    }

                }.bind(this)
            );
        },
        onSelectedNodeChanged: function (newNode) {
            d3.json(
                this.item_url() + encodeURIComponent(newNode.id()),
                function (error, response) {
                    if (error) {
                        showErrorModal(JSON.parse(error.responseText)['error'], false);
                    }
                    else if (this.graph().selectedNode().id() == newNode.id()) {
                        this.selectedObject.bind(this)(
                            new StixPackage(response["package"], response["root_id"], response["validation_info"])
                        );
                    }
                }.bind(this)
            )
        },
        onRowClicked: function () {
            // implements a click handler required by the review template. Does nothing here.
        },
        selectedTemplate: function () {
            var templateName = null;
            var selectedObject = this.selectedObject();
            if (selectedObject) {
                templateName = 'flat-' + selectedObject.type.code;
            }
            return templateName;
        },
        saveAsPNG: function (data, event) {
            PNGConverter.savetoPNG(event, this.rootId());
        }
    });
    ViewModel.loadById = function (/*String*/ rootId, /*String*/ graph_url, /*String*/ item_url, /*String*/ publish_url,
                                   /*PanelActions*/panel_actions, /*function*/ onLoadedCallback,
                                   /*function*/ onErrorCallback) {
        d3.json(
            graph_url + encodeURIComponent(rootId),
            function (error, response) {
                if (error) {
                    onErrorCallback(error);
                } else {
                    onLoadedCallback(new ViewModel(rootId, response, graph_url, item_url, publish_url, panel_actions));

                }
            }
        );
    };
    return ViewModel;
});
