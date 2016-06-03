define([
    "intern!object",
    "intern/chai!assert",
    "common/cert-abstract-builder-form",
    "common/tests/unit/mock/mock-validatable"
], function (registerSuite, assert, AbstractBuilderForm, MockValidatable) {
    "use strict";

    return registerSuite(function () {

        return {
            name: "common/cert-abstract-builder-form",
            "constructor": function () {
                assert.isDefined(AbstractBuilderForm);
            },
            "validation with error": function () {
                var abf = new AbstractBuilderForm();
                abf.validationGroup.push(new MockValidatable(true, "Error1"));
                abf.validationGroup.push(new MockValidatable(true, "Error2"));
                assert.isTrue(abf.doValidation().hasErrors());
                assert.equal(abf.doValidation().errors().length, 2);
            },
            "validation with no error": function () {
                var abf = new AbstractBuilderForm();
                abf.validationGroup.push(new MockValidatable(false, ""));
                abf.validationGroup.push(new MockValidatable(false, ""));
                assert.isFalse(abf.doValidation().hasErrors());
                assert.equal(abf.doValidation().errors().length, 0);
            },
            "call stubs": function () {
                var abf = new AbstractBuilderForm();
                abf.loadStatic();
                abf.counter();
                abf.load();
                abf.save();
            }
        }
    });
});

