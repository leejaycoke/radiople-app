app.controller('BaseController', function($scope, requestService, cookieService) {
    // get all user's broadcast    
    requestService.get('/broadcast', null, {
        success: function(response) {
            $scope.broadcasts = response.broadcasts;
            $scope.selectedBroadcastId = parseInt(cookieService.get('broadcast_id'));
        },
        error: function(error) {

        }
    });

    $scope.broadcastChanged = function() {
        var data = {'broadcast_id': $scope.selectedBroadcastId};
        requestService.put('/auth/current-broadcast', data, {
            success: function(response) {
                location.reload();
            },
            error: function(error) {

            }
        });
    }
});
