({
    appDir: "../../",
    baseUrl: "static/js",
    dir: "../../dist",
    paths: {
        knockout: "common/knockout-shim"
    },
    modules: [
        {
            name: "publisher/main"
        },
        {
            name: "config/config-main"
        },
        {
            name: "dedup/main"
        },
        {
            name: "ind-build/cert-ind-build-ready"
        },
        {
            name: "cert-identity"
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
