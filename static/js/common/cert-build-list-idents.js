define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-build-functions",
    "common/cert-identity"
], function (declare, ko, AbstractBuilderForm, buildFunctions, CERTIdentity) {
    "use strict";

    function ListIdents(label, options) {
        ListIdents.super.constructor.apply(this, [ label ]);

        this.saveKey = options['saveKey'];

        this.items = ko.observableArray([]);
        this.count = ko.computed(function () {
            return this.items().length || "";
        }, this);
    }

    buildFunctions.extend(ListIdents, AbstractBuilderForm);

    ListIdents.prototype.add = function() {
        var newItem = new CERTIdentity({name: 'Click to edit'});
        var items = this.items;
        newItem.ModelUI({viewModel:  newItem}).done(function(context, result){
            items.unshift(newItem);
        });
    };

     ListIdents.prototype.show_ui = function(model, data) {
         model.identity_model_ui({viewModel: data});
     }

    ListIdents.prototype.load = function(data) {
        this.items.removeAll();
        var self = this;
        if (this.saveKey in data) {
            $.each(data[this.saveKey], function(i,v) {
                self.items.push(new CERTIdentity(v['identity']));
            });
        }
    };

    ListIdents.prototype.remove = function(a) {
        this.items.remove(a);
    };

    ListIdents.prototype.save = function () {
        var data = {};
        var saveKey = this.saveKey;
        data[saveKey] = [];
        ko.utils.arrayForEach(this.items(), function(item) {
        	data[saveKey].push({'identity' : item.to_json()});
        });

        return data;
    };

    return  ListIdents;
});
