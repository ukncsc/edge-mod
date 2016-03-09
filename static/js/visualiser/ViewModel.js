define([
    "dcl/dcl",
    "knockout",
    "d3",
    "./graph/Graph",
    "./graph/forceGraphBinding"
], function (declare, ko, d3, Graph) {
    "use strict";

    var ViewModel = declare(null, {
        declaredClass: "ViewModel",
        constructor: function (rootId, graphData) {
            this.rootId = ko.computed(function () {
                return rootId;
            });
            this.graph = ko.observable(new Graph(graphData));
            this.selectedObject = ko.observable(null);
        },
        onNodeClicked: function (data) {
            d3.json(
                "/adapter/certuk_mod/ajax/visualiser/item/" + encodeURIComponent(data.id()),
                function (error, response) {
                    if (error) {
                        throw new Error(error);
                    }
                    this.selectedObject.bind(this)(response);
                }.bind(this)
            )
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
