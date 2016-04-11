define([
    "dcl/dcl",
    "knockout",
    "d3",
    "./graph/Graph",
    "../stix/StixPackage",
    "./graph/forceGraphBinding"
], function (declare, ko, d3, Graph, StixPackage) {
    "use strict";

    var ViewModel = declare(null, {
        declaredClass: "ViewModel",
        constructor: function (rootId, graphData, graph_url, item_url) {
            this.rootId = ko.computed(function () {
                return rootId;
            });
            this.graph_url = ko.computed(function () {
                return graph_url;
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
            this.graph().selectNode(data.id());
        },
        onSelectedNodeChanged: function (newNode) {
            d3.json(
                this.item_url() + encodeURIComponent(newNode.id()),
                function (error, response) {
                    if (error) {
                        throw new Error(error);
                    }
                    this.selectedObject.bind(this)(
                        new StixPackage(response["package"], response["root_id"], response["validation_info"])
                    );
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
        }
    });
    ViewModel.loadById = function (
        /*String*/ rootId, /*String*/ graph_url, /*String*/ item_url, /*function*/ onLoadedCallback, /*function*/ onErrorCallback
    ) {
        d3.json(
            graph_url + encodeURIComponent(rootId),
            function (error, response) {
                if (error) {
                    onErrorCallback(error);
                } else {
                    onLoadedCallback(new ViewModel(rootId, response, graph_url, item_url));
                }
            }
        );
    };
    return ViewModel;
});
