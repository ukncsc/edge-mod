define([
    "dcl/dcl",
    "knockout",
    "d3",
    "./graph/Graph",
    "../stix/StixPackage",
    "./toPNG/PNGConverter",
    "./graph/forceGraphBinding",
    "common/modal/show-error-modal"
], function (declare, ko, d3, Graph, StixPackage, PNGConverter, forceGraph, showErrorModal) {
    "use strict";

    var ViewModel = declare(null, {
        declaredClass: "ViewModel",

        constructor: function (rootId, graphData, graph_url, item_url, publish_url, graph_svg_id, panel_actions) {

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
            this.graph().backlinks.removeAll();
            this.graph().matches.removeAll();
            this.graph().edges.removeAll();
            this.graph().no_edges.removeAll();
            this.rootId = ko.computed(function () {
                return data;
            });
            this.getWithOthers();

        },
        onPlusBacklinkClicked: function (data, scope) {
            this.graph().backlinks.push(data);
            this.graph().findNode(data).isBackLinkShown(true);
            this.getWithOthers();
        },
        onMinusBacklinkClicked: function (data, scope) {
            this.graph().backlinks.remove(data);
            this.graph().findNode(data).isBackLinkShown(false);
            this.getWithOthers();
        },
        onShowEdges: function (data, scope) {
            this.graph().no_edges.remove(data);
            this.graph().edges.push(data);
            this.graph().findNode(data).isEdgesShown(true);
            this.getWithOthers();
        },
        onHideEdges: function (data, scope) {
            this.graph().no_edges.push(data);
            this.graph().edges.remove(data);
            this.graph().findNode(data).isEdgesShown(false);
            this.getWithOthers();
        },
        onPlusMatchesClicked: function (data, scope) {
            this.graph().matches.push(data);
            this.graph().findNode(data).isMatchesShown(true);
            this.getWithOthers();
        },
        onMinusMatchesClicked: function (data, scope) {
            this.graph().matches.remove(data);
            this.graph().findNode(data).isMatchesShown(false);
            this.getWithOthers();
        },
        getWithOthers: function () {
            postJSON(this.graph_url() + "get_extended/", {
                    'id': this.rootId(),
                    'id_bls': this.graph().backlinks(),
                    'id_matches': this.graph().matches(),
                    'hide_edge_ids': this.graph().no_edges(),
                    'show_edge_ids': this.graph().edges()
                }, function (result) {
                    this.graph().loadData(result);
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
                    else if (this.graph().selectedNode().id() == newNode.id()){
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

    ViewModel.loadById = function (/*String*/ rootId, /*String*/ graph_url, /*String*/ item_url, /*String*/ publish_url, /*String*/ graph_svg_id,
                                   /*PanelActions*/panel_actions, /*function*/ onLoadedCallback,
                                   /*function*/ onErrorCallback) {
        d3.json(
            graph_url + encodeURIComponent(rootId),
            function (error, response) {
                if (error) {
                    onErrorCallback(error);
                } else {
                    onLoadedCallback(new ViewModel(rootId, response, graph_url, item_url, publish_url, graph_svg_id, panel_actions));

                }
            }
        );
    };
    return ViewModel;
});
