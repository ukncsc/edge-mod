define([
    "../dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-build-functions"
], function (declare, ko, AbstractBuilderForm, buildFunctions) {
    "use strict";

    function ListSelects(label, options) {
        ListSelects.super.constructor.apply(this, [ label ]);
        this.saveKey = options['saveKey'];
        this.selectChoiceName = options['selectChoice'];
        this.options = ko.observableArray();

        this.items = ko.observableArray().extend({ rateLimit: 200 });
        this.dragging = ko.observable(false);

        this.sourceSelect = ko.observable();
        this.targetSelect = ko.observable();

        this.count = ko.computed(function () {
            return this.items().length || "";
        }, this);

        this.dragging.subscribe(function(dragging) {
            if (dragging) {
                document.body.style.cursor = 'no-drop';
                self.sourceSelect().style.cursor = "move";
                self.targetSelect().style.cursor = "move";
            } else {
                self.sourceSelect().style.cursor = "default";
                self.targetSelect().style.cursor = "default";
                document.body.style.cursor = 'default';
            }
        }, this);

        this.remaining_items = ko.computed(function () {
            var tempArray = ko.observableArray(this.options().slice(0));
            tempArray.removeAll(this.items());
            return tempArray();
        }, this);

        var self = this;
        //global mouseup handler to stop dragging
        document.documentElement.addEventListener('mouseup', function(e){
            self.dragging(false);
            return true;
        });
    }

    buildFunctions.extend(ListSelects, AbstractBuilderForm);

    ListSelects.prototype.loadStatic = function (optionLists) {
        this.options(optionLists[this.selectChoiceName]);
    };

     ListSelects.prototype.onMouseDown = function(d, e)
     {
        //Override base behaviour so clicking on selected items doesn't clear other selected items
        return e.target.selected != true
     };

     ListSelects.prototype.onMouseUp = function(d, e)
     {
         if (this.dragging()) {
             if (e.target === this.sourceSelect() || e.target.parentNode === this.sourceSelect()) {
                 d.remove();
             } else {
                 d.add();
             }
         }

         this.dragging(false);
         return true;
     };

     ListSelects.prototype.onMouseMove = function(d, e)
     {
         //Already dragging
         if (this.dragging()) {
             return false;
         }

         //Start dragging
        if (e.target.selected === true && e.buttons == 1) {
           this.dragging(true);
           return false;
        }

        return true;
     };

    ListSelects.prototype.load = function(data) {
        this.items.removeAll();
        var self = this;
        if (self.saveKey in data) {
            $.each(data[self.saveKey], function(i,v) {
                self.items.push(v);
            });
        }
    };

    ListSelects.prototype.add = function() {
        var left_select = this.sourceSelect()
        for (var i=0;i<left_select.length;i++){
            if (left_select.options[i].selected) {
                this.items.push(left_select.options[i].label);
            }
        }
    };

    ListSelects.prototype.remove = function(a) {
        var self = this;
        var right_select = this.targetSelect();
        for (var i=0;i<right_select.length;i++){
            if (right_select.options[i].selected) {
                self.items.remove(right_select.options[i].label);
            }
        }

    };

    ListSelects.prototype.save = function () {
        var data = {};
        var saveKey = this.saveKey;
        data[saveKey] = [];
        ko.utils.arrayForEach(this.items(), function(item) {
        	data[saveKey].push(item);
        });

        return data;
    };

    return  ListSelects;
});

ko.bindingHandlers.listSelectElement = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var elemObservable = valueAccessor();
        if (ko.isObservable(elemObservable)) {
			elemObservable(element);
		}
    }
};