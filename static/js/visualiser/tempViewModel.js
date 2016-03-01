var viewModel = {};

var _yByDepth = [0];
function yByDepth(depth) {
    return _yByDepth[depth] = (_yByDepth[depth] || 0) + 100;
}

d3.json("/adapter/certuk_mod/ajax/visualiser/" + encodeURIComponent(stixId),
    function (error, response) {
        if (error) {
            throw error;
        }
        if (!response.success) throw new Error(response.error_message);
        viewModel.graph = ko.observable(response.graph);
        var graph = viewModel.graph();
        var rootNode = graph.nodes[0];
        rootNode.isRoot = true;
        rootNode.x = 40;
        rootNode.y = 260;
        rootNode.fixed = true;

        // If positions are not set, D3 will assign random values, which
        // ensures nodes spread out "evenly" during simulation. However, this
        // means their positions are not deterministic. The code below shoves
        // all other nodes in the corner, in practice we'd probably want to do
        // something a bit more clever.
        for (var i = 1, len = graph.nodes.length; i < len; i++) {
            var node = graph.nodes[i];
            node.x = node.depth * 200;
            node.y = yByDepth(node.depth);
        }

        ko.applyBindings(viewModel);
    });
