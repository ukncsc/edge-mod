define([
    "knockout"
], function (ko) {
    var createModalElement = function (templateName, viewModel) {
        var temporaryDiv = addHiddenDivToBody();
        var deferredElement = $.Deferred();
        ko.setTemplateEngine(new ko.nativeTemplateEngine);
        ko.renderTemplate(
            templateName,
            viewModel,
            {
                afterRender: function (nodes) {
                    var elements = nodes.filter(function (node) {
                        return node.nodeType === 1;
                    });
                    deferredElement.resolve(elements[0]);
                }
            },
            temporaryDiv,
            "replaceNode"
        );
        return deferredElement;
    };

    var addHiddenDivToBody = function () {
        var div = document.createElement("div");
        div.style.display = "none";
        document.body.appendChild(div);
        return div;
    };

    var showModal = function (options) {
        if (typeof options === 'undefined') throw new Error('An options argument is required');
        if (typeof options.viewModel !== 'object') throw new Error('options.viewModel is required');

        var viewModel = options.viewModel;
        var template = options.template || viewModel.template;
        var context = options.context;

        if (!template) throw new Error('options.template or options.viewModel.template is required');

        return createModalElement(template, viewModel)
            .pipe($)
            .pipe(function ($ui) {
                var deferredModalResult = $.Deferred();
                addModalHelperToViewModel(viewModel, deferredModalResult, context);
                showTwitterBootstrapModal($ui);
                whenModalResultCompleteThenHideUI(deferredModalResult, $ui);
                whenUIHiddenThenRemoveUI($ui);
                return deferredModalResult;
            });
    };

    var addModalHelperToViewModel = function (viewModel, deferredModalResult, context) {
        viewModel.modal = {
            close: function (result) {
                if (typeof result !== 'undefined') {
                    deferredModalResult.resolveWith(context, [result]);
                } else {
                    deferredModalResult.rejectWith(context, []);
                }
            }
        };
    };

    var showTwitterBootstrapModal = function ($ui) {
        $ui.modal({
            backdrop: 'static',
            keyboard: false
        });
    };

    var whenModalResultCompleteThenHideUI = function (deferredModalResult, $ui) {
        deferredModalResult.always(function () {
            $ui.modal('hide');
        });
    };

    var whenUIHiddenThenRemoveUI = function ($ui) {
        $ui.on('hidden.bs.modal', function () {
            $ui.each(function (index, element) {
                ko.cleanNode(element);
            });
            $ui.remove();
        });
    };
    return showModal;
});
