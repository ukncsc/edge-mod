define(["knockout-3.1.0", "dcl/dcl"], function (ko, declare) {

    function filterIncidentObject (response) {
        var incident = {};
        ko.utils.objectForEach(response||{}, function (name, value) {
            if (name === "edges") {
                incident.edges = ko.utils.arrayFilter(value, function (edge) {
                    var type = edge["ty"];
                    return type === "ttp" || type === "ind"
                        || type === "coa" || type === "inc";
                })
            } else if (name === "success" || name === "error_message") {
                // ignore these properties
            } else {
                incident[name] = value;
            }
        });
        return incident;
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
            this.selectedEdges = ko.observableArray([]);

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
            this.selectedEdges.removeAll();
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
        }
    });
});
