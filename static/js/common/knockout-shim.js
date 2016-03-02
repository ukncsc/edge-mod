define([], function () {
    "use strict";

    ko.extenders.validate = function (target, options) {
        var isValidCallback = options['isValidCallback'];
        var failedValidationMessage = options['failedValidationMessage'];
        var failedValidationDisplayMessage = options['failedValidationDisplayMessage'];
        target.hasError = ko.observable(false);
        target.errorMessage = ko.observable("");
        target.displayErrorMessage = ko.observable("");
        target.hasValidation = true;

        function validate() {
            var isValid = isValidCallback(target());

            target.hasError(!isValid);
            target.errorMessage(isValid ? "" : failedValidationMessage);
            target.displayErrorMessage(isValid ? "" : failedValidationDisplayMessage);
        }

        target.subscribe(validate);
        validate();

        return target;
    };

    ko.extenders.required = function (target, required) {
        if (required === true) {
            return ko.extenders.validate(target, {
                isValidCallback: function (value) {

                    return (typeof value === "string" && value.trim().length > 0) || isFinite(parseFloat(value));
                },
                failedValidationMessage: "* (Required)"
            });
        }
        return target;
    };

    ko.extenders.requiredGrouped = function (target, options) {
        if (options['required'] === true) {
            options['group'].push(target);
            var displayMessage = options['displayMessage'];
            return ko.extenders.validate(target, {
                isValidCallback: function (value) {
                    if (Array.isArray(value)) {
                        return value.length != 0;
                    }
                    return (typeof value === "string" && value.trim().length > 0) || isFinite(parseFloat(value));
                },
                failedValidationMessage: "* (Required)",
                failedValidationDisplayMessage: displayMessage
            });

        }


        return target;
    };


    ko.bindingHandlers.highlightedText = {
        update: function (element, valueAccessor) {
            var options = valueAccessor();
            var search = ko.utils.unwrapObservable(options.match);
            search = search.trim().replace(/\s/g, "|");
            search = "\\b(" + search + ")\\b";
            var value = ko.utils.unwrapObservable(options.text);
            var css = ko.utils.unwrapObservable(options.css);
            element.innerHTML = value.replace(new RegExp(search, 'gi'), '<span class="' + css + '">' + '$&' + '</span>');
        }
    };

    ko.onDemandObservable = function (callback, target) {
        // Perhaps pass this in, making this function a wrapper on existing observables..?
        var _value = ko.observableArray();

        var result = ko.computed({
            read: function () {
                if (!result.loaded()) {
                    callback.call(target);
                }

                return _value();
            },
            write: function (newValue) {
                result.loaded(true);
                _value(newValue);
            },
            deferEvaluation: true
        });

        result.loaded = ko.observable();
        // Could make this a computed observable, so it would refresh automatically?
        result.refresh = function () {
            result.loaded(false);
        };

        return result;
    };

    ko.bindingHandlers.effectOnChange = {
        update: function (element, valueAccessor, allBindings) {
            var value = valueAccessor();
            var applyEffectOnEmpty = allBindings.get('applyEffectOnEmpty') === 'true';
            if (applyEffectOnEmpty || ko.unwrap(value)) {
                var effect = allBindings.get('effectName') || 'shake';
                $(element).effect(effect);
            }
        }
    };

    return window.ko;
});
