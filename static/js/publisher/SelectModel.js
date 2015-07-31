define(["knockout", "knockout-dragdrop", "dcl/dcl"], function (ko, kos, declare) {
    "use strict";

    function filterIncidentObject(response) {
        var incident = {};
        ko.utils.objectForEach(response || {}, function (name, value) {
            if (name === "edges") {
                ko.utils.arrayForEach(value, function (edge, idx) {
                    var nextEdge = value[idx + 1];
                    edge._isParent = !!nextEdge && nextEdge.depth === (edge.depth + 1);
                    var type = edge["ty"];
                    edge._selectable = (type === "obs" || type === "ttp" || type === "ind" || type === "coa" || type === "inc");
                    edge._selected = ko.observable(false);
                });
                incident.edges = value;
            } else if (name === "success" || name === "error_message") {
                // ignore these properties
            } else {
                incident[name] = value;
            }
        });
        return incident;
    }

    function getEdges(self) {
        return (self.selectedIncident() || {}).edges || [];
    }

    function hasUnselectedChildren(edges, edge) {
        var hasUnselectedChildren = false;
        var idx = ko.utils.arrayIndexOf(edges, edge);
        if (idx > -1) {
            for (var i = idx + 1, len = edges.length; hasUnselectedChildren === false && i < len; i++) {
                if (edges[i].depth > edge.depth) {
                    hasUnselectedChildren = (edges[i]._selected() === false);
                } else {
                    break;
                }
            }
        }
        return hasUnselectedChildren;
    }

    return declare(null, {
        constructor: function () {
            this.search = ko.observable("");
            this.results = ko.observableArray([]);
            this.hasResults = ko.computed(function () {
                return this.results().length > 0;
            }, this);
            this.selectedId = ko.observable("");
            this.selectedIncident = ko.observable(null);

            this.availableEdges = ko.computed(function () {
                var edges = getEdges(this);
                return ko.utils.arrayFilter(edges, function (edge) {
                    return edge._selected() === false
                        || (edge._isParent === true && hasUnselectedChildren(edges, edge));
                });
            }.bind(this));
            this.selectedEdges = ko.computed(function () {
                return ko.utils.arrayFilter(getEdges(this), function (edge) {
                    return edge._selected() === true;
                });
            }.bind(this));

            this.search.subscribe(this._onSearchChanged, this);
            this.selectedId.subscribe(this._onSelectionChanged, this);

            this._onSearchChanged(this.search());
        },

        _onSearchChanged: function (/*String*/ newValue) {
            postJSON("/catalog/ajax/load_catalog/", {
                search: newValue,
                size: 10,
                type: "inc"
            }, this._onSearchResponseReceived.bind(this));
        },

        _onSearchResponseReceived: function (response) {
            if (response["success"]) {
                this.results(response["data"]);
            } else {
                alert(response["message"]);
            }
        },

        select: function (incident) {
            this.selectedId(incident.id);
        },

        unselect: function () {
            this.selectedId(null);
        },

        _onSelectionChanged: function (newId) {
            if (newId) {
                postJSON("/catalog/ajax/get_object/", {
                    id: newId
                }, this._onSelectionResponseReceived.bind(this));
            } else {
                this.selectedIncident(null);
            }
        },

        _onSelectionResponseReceived: function (response) {
            if (response["success"]) {
                this.selectedIncident(filterIncidentObject(response));
            } else {
                alert(response["error_message"]);
            }
        },

        onSelected: function (data, model) {
            if (data._selectable === true) {
                data._selected(true);
            }
        },

        onUnselected: function (data, model) {
            data._selected(false);
        },

        getIndent: function (edge) {
            return edge._selected() === true ? "0" : (edge.depth * 12) + "px";
        },

        isEnabled: function (edge) {
            return edge._selectable === true && edge._selected() === false;
        },

        canPublish: function() {
            return true;//this.selectedEdges().length > 0;
        },

        publish: function() {
            postJSON("/adapter/publisher/ajax/publish/", {
                object_ids: this.selectedEdges().map(function (edge) {
                    return edge.id_;
                }).concat(this.selectedId()),
                package_info: {
                    title: 'TEST PACKAGE',
                    description: 'Package description goes here...',
                    short_description: 'Short description :)'
                }
            }, this._onPublishResponseReceived.bind(this));
        },

        _onPublishResponseReceived: function(response) {
            alert(response['message']);
            if (response['success']) {
                this.selectedIncident(null);
            }
        }
    });
});
