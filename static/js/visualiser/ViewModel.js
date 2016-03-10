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
        constructor: function (rootId, graphData) {
            this.rootId = ko.computed(function () {
                return rootId;
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
            this.graph().selectNode(rootId);
        },
        onNodeClicked: function (data) {
            this.graph().selectNode(data.id());
        },
        onSelectedNodeChanged: function (newNode) {
            d3.json(
                "/adapter/certuk_mod/ajax/visualiser/item/" + encodeURIComponent(newNode.id()),
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
            // do nothing
        },
        selectedTemplate: function () {
            var templateName = null;
            var selectedObject = this.selectedObject();
            if (selectedObject) {
                templateName = 'root-' + selectedObject.type.code;
            }
            return templateName;
        }
    });
    ViewModel.loadById = function (/*String*/ rootId, /*function*/ onLoadedCallback) {
        d3.json(
            "/adapter/certuk_mod/ajax/visualiser/" + encodeURIComponent(rootId),
            function (error, response) {
                if (error) {
                    throw new Error(error);
                }
                onLoadedCallback(new ViewModel(rootId, response));
            }
        );
    };
    return ViewModel;
});
