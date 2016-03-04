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
        }
    });
    ViewModel.loadById = function (/*String*/ rootId, /*function*/ onLoadedCallback) {
        d3.json(
            "/adapter/certuk_mod/ajax/visualiser/" + encodeURIComponent(rootId),
            function (error, response) {
                if (error || !response.success) {
                    throw new Error(error || response.error_message);
                }
                onLoadedCallback(new ViewModel(rootId, response.graph));
            }
        );
    };
    return ViewModel;
});
