define([
    "dcl/dcl",
    "knockout",
    "d3",
    "visualiser/foreachGraphNodeBinding"
], function (declare, ko, d3) {
    "use strict";

/*
    var _yByDepth = [0];
    function yByDepth(depth) {
        return _yByDepth[depth] = (_yByDepth[depth] || 0) + 100;
    }
*/

    var ViewModel = declare(null, {
        declaredClass: "ViewModel",
        constructor: function (rootId, graph) {
            this.rootId = ko.computed(function () {
                return rootId;
            });
            this.graph = ko.observable(graph);
        }
    });
    ViewModel.loadById = function (/*String*/ rootId, /*function*/ onLoadedCallback) {
        d3.json(
            "/adapter/certuk_mod/ajax/visualiser/" + encodeURIComponent(rootId),
            function (error, response) {
                if (error || !response.success) {
                    throw new Error(error || response.error_message);
                }
                var graph = response.graph;
                var rootNode = graph.nodes[0];
                rootNode.isRoot = true;
/*
                rootNode.fixed = true;
                rootNode.x = 0;
                rootNode.y = 0;
                for (var i = 1, len = graph.nodes.length; i < len; i++) {
                    var node = graph.nodes[i];
                    node.x = node.depth * 100;
                    node.y = yByDepth(node.depth);
                }
*/
                onLoadedCallback(new ViewModel(rootId, graph));
            }
        );
    };
    return ViewModel;
});
