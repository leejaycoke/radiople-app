app.controller('ViewController', function($scope, $httpParamSerializerJQLike, cookieService, requestService) {
    requestService.get('/broadcast', null, {
        success: function(response) {
            $scope.broadcast = response;
        }
    });

    requestService.get('/category', null, {
        success: function(response) {
            $scope.categories = response.categories;
        }
    });

    $scope.edit = function() {
        requestService.put('/broadcast', $scope.broadcast, {
            success: function(response) {
                alert("성공적으로 수정되었습니다.");
                location.reload();
            },
            error: function(error) {
                $scope.errorMessage = error.display_message;
            }
        });
    }

    $scope.deleteIconImage = function() {
        $scope.broadcast.icon_image = null;
    }

    $scope.uploadImage = function(image, callback, url) {
        if (!image) {
            return false;
        }

        var url = url + "?" + $httpParamSerializerJQLike({
            service: 'console',
            access_token: cookieService.get('access_token')
        });

        requestService.upload('PUT', url, {
            file: image
        }, {
            success: function(response) {
                callback(response);
            },
            error: function(error) {
                alert("업로드 할 수 없습니다.");
            },
        });
    }

    $scope.iconImageCallback = function(response) {
        $scope.broadcast.icon_image = response.url;
    }

    $scope.coverImageCallback = function(response) {
        $scope.broadcast.cover_image = response.url;
    }

    $scope.addCasting = function() {
        $scope.broadcast.casting.push("");
    }

    $scope.removeCasting = function(index) {
        $scope.broadcast.casting.splice(index, 1);
    }
});
