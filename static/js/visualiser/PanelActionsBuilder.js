define([
    "dcl/dcl",
    "knockout",
    "visualiser/PanelAction",
    "visualiser/PanelActions"
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
            ko.utils.arrayForEach(this.actions(), function(item) {
                pa.addAction(item);
            })
            return pa;
        }
    })
});
