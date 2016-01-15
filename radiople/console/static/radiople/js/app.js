var app = angular.module('RadiopleApplication', ['ui.bootstrap', 'ngFileUpload', 'ngCookies', 'ui.bootstrap.datetimepicker', 'ngHolder']);

app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
});

app.filter('appendSize', function() {
    return function(imageUrl, width, height) {
        if (!imageUrl) {
            return null;
        }
        var url = new URL(imageUrl);
        return url.protocol + '//' + url.host + '/' + width + 'x' + height + url.pathname;
    };
});

app.directive('ngEnter', function() {
    return function(scope, element, attrs) {
        element.bind("keydown keypress", function(event) {
            if (event.which === 13) {
                scope.$apply(function() {
                    scope.$eval(attrs.ngEnter);
                });

                event.preventDefault();
            }
        });
    };
});

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
}]);
