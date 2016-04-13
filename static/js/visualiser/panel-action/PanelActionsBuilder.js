define([
    "../../dcl/dcl",
    "knockout",
    "visualiser/panel-action/PanelAction",
    "visualiser/panel-action/PanelActions"
], function (declare, ko, PanelAction, PanelActions) {
    "use strict";

    return declare(null, {
        declaredClass: "PanelActionsBuilder",
        constructor: function () {
            this.actions = ko.observableArray([])
        },
        addAction: function(newAction){
            this.actions.push(newAction);
            return this;
        },
        build: function(){
            var pa = new PanelActions()
            pa.actions(this.actions());
            return pa;
        }
    })
});
