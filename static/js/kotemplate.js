define(["text"], function (text) {
    "use strict";

    function parse(name) {
        var parts = name.split(":", 2);
        return {
            id: parts[0],
            name: parts[1]
        }
    }

    return {
        version: "0.0.1",

        load: function (name, parentRequire, onLoad, config) {
            var params = parse(name);
            text.load(params.name, parentRequire, function (templateText) {
                var scriptTag = document.createElement("script");
                scriptTag.setAttribute("type", "text/html");
                scriptTag.setAttribute("id", params.id);
                scriptTag.appendChild(document.createTextNode(templateText));
                document.body.appendChild(scriptTag);
                onLoad({
                    id: params.id,
                    template: templateText
                });
            }, config);
        }
    };
});
