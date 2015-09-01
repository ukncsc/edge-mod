define(["text"], function (text) {
    "use strict";

    var buildMap = {};

    function parse(name) {
        var parts = name.split(":", 2);
        return {
            id: parts[0],
            name: parts[1]
        }
    }

    function isBrowser() {
        return !(typeof document === "undefined");
    }

    return {
        version: "1.0.0",

        normalize: function (name, normalize) {
            var params = parse(name);
            return params.id + ":" + normalize(params.name);
        },

        load: function (name, parentRequire, onLoad, config) {
            var params = parse(name);
            text.load(params.name, parentRequire, function (templateText) {
                if (config.isBuild) {
                    buildMap[params.id] = templateText;
                } else if (isBrowser()) {
                    var scriptTag = document.createElement("script");
                    scriptTag.setAttribute("type", "text/html");
                    scriptTag.setAttribute("id", params.id);
                    scriptTag.appendChild(document.createTextNode(templateText));
                    document.body.appendChild(scriptTag);
                }
                onLoad();
            }, config);
        },

        write: function (pluginName, moduleName, write) {
            var params = parse(moduleName);
            write.asModule(
                pluginName + "!" + moduleName,
                    "define(function () {" +
                        "var scriptTag = document.createElement('script');" +
                        "scriptTag.setAttribute('type', 'text/html');" +
                        "scriptTag.setAttribute('id', '" + params.id + "');" +
                        "scriptTag.appendChild(document.createTextNode('" + text.jsEscape(buildMap[params.id]) + "'));" +
                        "document.body.appendChild(scriptTag);" +
                    "});"
            );
        }
    };
});
