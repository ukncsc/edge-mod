({
    appDir: "../../",
    baseUrl: "static/js",
    dir: "../../dist",
    paths: {
        knockout: "empty:"
    },
    modules: [
        {
            name: "publisher/main"
        },
        {
            name: "publisher/config-main"
        }
    ],
    fileExclusionRegExp: /^\.|^tests$|^build.js$|\.md$/,
    locale: "en-gb",
    optimize: "uglify2",
    skipDirOptimize: true,
    inlineText: true,
    useStrict: true,
    removeCombined: true
})
