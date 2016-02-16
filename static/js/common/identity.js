define([
    "dcl/dcl",
    "knockout",
    "common/cert-abstract-builder-form",
    "common/cert-build-functions"
], function (declare, ko, AbstractBuilderForm, buildFunctions) {
    "use strict";

    function EdgeIdentity() {
        EdgeIdentity.super.constructor.call(this, "EdgeIdentity");
        this.name = ko.observable().extend({ required: true});
        this.roles = ko.observableArray([]);
        this.electronic_address_identifiers = ko.observableArray([]);
        this.party_name = ko.observable();
        this.languages = ko.observableArray([]);
        this.free_text_lines = ko.observableArray([]);
        this.template = "identity-element-popup";
        this.electronic_address_type = ko.observable();
        this.electronic_address_types = ko.observableArray([]);
    }

    buildFunctions.extend(EdgeIdentity, AbstractBuilderForm);

    EdgeIdentity.prototype.loadStatic = function (optionLists){
        this.electronic_address_types(optionLists.electronic_address_types);
    };

    EdgeIdentity.prototype.load = function (data) {
        this.name(buildFunctions.getField(data, "name") || "");
        this.roles(buildFunctions.getField(data, "roles") || []);
        this.electronic_address_identifiers(buildFunctions.getField(data, "specification.electronic_address_identifiers") || []);
        this.party_name(buildFunctions.getField(data, "specification.name") || "");
        this.languages(buildFunctions.getField(data, "specification.languages") || []);
        this.free_text_lines(buildFunctions.getField(data, "specification.free_text_lines") || []);
        this.template("identity-element-popup");
        this.electronic_address_type(buildFunctions.getField(data, "electronic_address_type") || "");
    };

    EdgeIdentity.prototype.addRole = function() {
         if(buildFunctions.arrayisFull(this.roles())){
             this.roles.unshift("");
         }
    };

    EdgeIdentity.prototype.addLanguage = function() {
         if(buildFunctions.arrayisFull(this.languages())){
             this.languages.unshift("");
         }
    };

    EdgeIdentity.prototype.addText = function() {
         if(buildFunctions.arrayisFull(this.free_text_lines())){
             this.free_text_lines.unshift("");
         }
    };

    EdgeIdentity.prototype.addEAddress = function() {
         if(!buildFunctions.arrayHasEmptyEmailAddresses(this.electronic_address_identifiers())){
             this.electronic_address_identifiers.unshift({value: '', type: ''});
         }
    };

    EdgeIdentity.prototype.createSnapshot = function() {
		this.previousState = this.clone();
	};

	EdgeIdentity.prototype.restoreSnapshot = function() {
		for (var key in this.previousState) {
			if (this.previousState.hasOwnProperty(key)) {
				this[key](this.previousState[key])
			}
		}
	};

	EdgeIdentity.prototype.okay = function() {
		if(!is_string.test(this.name())) {
			$('#identity_name').parent().append(alert_danger("This field may not be empty and may only contain letters, numbers and spaces"));
			return;
		}
		this.modal.close(this.newIdentity());
	};

	EdgeIdentity.prototype.cancel = function() {
		this.restoreSnapshot(this.previousState);
		this.modal.close(this.previousState);
	};


    EdgeIdentity.prototype.clone = function() {
		return {
			name: this.name(),
			party_name: this.party_name(),
			roles: this.roles().slice(),
			languages: this.languages().slice(),
			electronic_address_identifiers: this.electronic_address_identifiers().slice(),
			free_text_lines: this.free_text_lines().slice()
		};
	};

    EdgeIdentity.prototype.to_json = function() {
        if(this.name())
		{
			return {
                name: this.name(),
                roles: this.roles(),
                specification: {
                    party_name: {
                          names_lines: [{
                              value: this.party_name(),
                              type: 'string'
                          }]
                    },
                    languages: this.languages().map(function(obj) {
                        return {
                            value: obj
                        }
                    }),
                    free_text_lines: this.free_text_lines().map(function(obj) {
                        return {
                            value: obj,
                            type: 'string'
                        }
                    }),
                    electronic_address_identifiers: this.electronic_address_identifiers()
                }
            };
		} else {
			return undefined
		}
    };

    return EdgeIdentity;

});
