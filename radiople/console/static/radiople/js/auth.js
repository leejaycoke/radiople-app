app.controller('SigninController', function($scope, $cookies, $location, requestService) {
    $scope.signin = function() {
        $scope.isSigning = true;
        $scope.error = null;

        requestService.post('/auth/signin', $scope.user, {
            success: function(response) {
                location.replace('/dashboard/index.html');
            },
            error: function(error) {
                $scope.error = error.display_message;
                $scope.isSigning = false;
            }
        });
    };
});