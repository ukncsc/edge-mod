# Testing with [Intern](https://theintern.github.io/)

## Prerequisites

* `sudo yum install node npm`
* `sudo npm install -g intern nodemon`

## Running the tests manually

* from the root of your project, run: `nodemon /usr/bin/intern-runner config=tests/intern`
* point you browser at [http://localhost:9000/__intern/client.html?initialBaseUrl=/&config=tests/intern](http://localhost:9000/__intern/client.html?initialBaseUrl=/&config=tests/intern)

## Integration with PyCharm

* install the `NodeJS` plugin
* _optionally install the `Markdown` plugin to more easily view this document_
* restart PyCharm
* create a `Node.js` run configuration as follows:
    * Configuration
        <table><tbody>
        <tr><td>Node interpreter</td><td>`/usr/bin/nodemon`</td></tr>
        <tr><td>Node parameters</td><td><em>leave blank</em></td></tr>
        <tr><td>Working directory</td><td><em>project root</em></td></tr>
        <tr><td>JavaScript file</td><td>`/usr/bin/intern-runner`</td></tr>
        <tr><td>Application parameters</td><td>`config=tests/intern`</td></tr>
        <tr><td>Environment variables</td><td><em>leave blank</em></td></tr>
        </tbody></table>
    * Browser / Live Edit
        * tick `After launch`
        * select your preferred browser
        * set URL to: `http://localhost:9000/__intern/client.html?initialBaseUrl=/&config=tests/intern`

## Useful links

* [Intern](https://theintern.github.io/intern/)
    * [User Guide](https://theintern.github.io/intern/)
        * [Writing a unit test](https://theintern.github.io/intern/#writing-unit-test)
        * [Writing a functional test](https://theintern.github.io/intern/#writing-functional-test)
* [Chai Assertion Library](http://chaijs.com)
    * [`assert` API reference](http://chaijs.com/api/assert/)
