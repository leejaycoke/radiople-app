app.controller('ResetPasswordController', function($scope, requestService) {
    $scope.send = function() {
        $scope.isSending = true;
        $scope.error = null;

        if ($scope.user.password != $scope.user.confirmPassword) {
            $scope.error = "비밀번호가 서로 일치하지 않습니다.";
            $scope.isSending = false;
        }

        requestService.post('#', $scope.user, {
            success: function(response) {
                location.replace('/');
            },
            error: function(error) {
                $scope.error = error;
                $scope.isSending = false;
            }
        });
    }
});