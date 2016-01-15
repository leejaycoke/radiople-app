var app = angular.module('RadiopleApplication', ['ui.bootstrap', 'ngFileUpload']);

app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});