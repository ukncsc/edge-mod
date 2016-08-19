({
    appDir: "../../",
    baseUrl: "static/js",
    dir: "../../dist",
    paths: {
        d3: "empty:",
        jquery: "common/jquery-shim",
        knockout: "common/knockout-shim",
        "config-service": "empty:"
    },
    modules: [
        {
            name: "catalog/cert-catalog-build-ready"
        },
        {
            name: "config/config-main"
        },
        {
            name: "dedup/main"
        },
        {
            name: "activity-log/main"
        },
        {
            name: "inc-build/cert-inc-build-ready"
        },
        {
            name: "ind-build/cert-ind-build-ready"
        },
        {
            name: "clone-build/cert-clone-build-ready"
        },
        {
            name: "visualiser/main"
        },
        {
            name: "extract/upload/main"
        },
        {
            name: "extract/visualise/main"
        },
        {
            name: "extract/status/main"
        },
        {
            name: "timeline/incident_main"
        }
    ],
    fileExclusionRegExp: /^\.|^tests$|^build.js$|\.md$|\.pyc$/,
    locale: "en-gb",
    optimize: "uglify2",
    skipDirOptimize: true,
    inlineText: true,
    useStrict: true,
    removeCombined: true
})
