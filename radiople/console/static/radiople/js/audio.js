app.controller('ListController', function($scope, uploadService) {
    $scope.pageChanged = function() {
        location.href = '?page=' + $scope.paging.page;
    }

    // $scope.search = function() {
    //     location.href = '/audio/list?' + serialize($scope.paging);
    // }

    // $scope.show = function() {
    //     alert('good');
    // }
    $scope.view = function(filename) {
        window.location.href = filename;
    }
});

app.controller('CreateController', function($scope, $cookies, requestService) {
    $scope.isUploading = false;
    $scope.progress = 0;

    $scope.upload = function(uploadUrl) {
        $scope.isUploading = true;
        $scope.uploadedFilename = null;
        $scope.uploadError = null;

        // uploadService.upload(uploadUrl, $cookies.get('session'), $scope.audioFile, {
        //     progress: function(percent) {
        //         $scope.progress  = percent;
        //     },
        //     success: function(data) {
        //         $scope.uploadedFilename = $scope.audioFile.name;
        //         $scope.audioFile = null;
        //     },
        //     error: function(error) {
        //         $scope.uploadError = error;
        //     },
        //     then: function(data) {
        //         $scope.isUploading = false;
        //         $scope.progress = 0;
        //     }
        // });
    }
});

app.controller('ViewController', function($scope, requestService) {
    $scope.isUsingAudio = true;

    $scope.editAudio = function() {
        var data = {
            'upload_filename': $scope.upload_filename
        };

        var success = function() {
            $scope.successMessage = "수정되었습니다.";
        }

        var error = function(message) {
            $scope.errorMessages = message;
        }

        requestService.put('#', data, success, error);
    }

    $scope.changedUploadFilename = function() {
        var filename = $scope.upload_filename
        $scope.upload_filename = $scope.upload_filename + '.mp3';
    }
});
