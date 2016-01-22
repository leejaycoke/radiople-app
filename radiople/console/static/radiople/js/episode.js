app.controller('ListController', function($scope, $httpParamSerializerJQLike, cookieService, requestService) {

    $scope.episodes = [];
    $scope.paging = {};

    $scope.requestEpisodeList = function() {
        var params = {
            page: $scope.paging.page,
            q: $scope.q
        }

        requestService.get('/episode', params, {
            success: function(response) {
                $scope.episodes = response.item;
                $scope.paging = response.paging;
            },
            error: function(error) {
                alert(error.display_message);
            }
        });
    }

    $scope.requestEpisodeList();

    $scope.create = function() {
        location.href = '/episode/create.html';
    }

    $scope.edit = function(episodeId) {
        location.href = '/episode/edit.html?episode_id=' + episodeId
    }

    $scope.pageChanged = function() {
        $scope.requestEpisodeList();
    }

    $scope.search = function() {
        $scope.requestEpisodeList();
    }

});

app.controller('CreateController', function($scope, $filter, $httpParamSerializerJQLike, requestService, cookieService) {
    $scope.dateOptions = {
        showWeeks: false,
        startDay: 1
    }

    $scope.timeOptions = {
        showMeridian: false
    }

    $scope.episode = {};

    $scope.airDateChanged = function() {
        $scope.episode.air_date = $filter('date')($scope.episode.air_date, 'yyyy-MM-dd HH:mm');
    };

    $scope.progress = 0;

    $scope.upload = function(url) {
        $scope.isUploading = true;
        $scope.audioErrorMessage = null;

        var url = url + "?" + $httpParamSerializerJQLike({
            service: 'console',
            access_token: cookieService.get('access_token')
        });

        requestService.upload('PUT', url, {
            file: $scope.audioFile
        }, {
            success: function(audio) {
                $scope.episode.audio = audio;
                $scope.episode.audio_id = audio.id;
            },
            error: function(error) {
                alert(error.display_message);
            },
            progress: function(p) {
                if (p < 100) {
                    $scope.progress = p;
                } else {
                    $scope.progress = "데이터 확인중.."
                }
            },
            then: function(audio) {
                $scope.progress = 0;
                $scope.isUploading = false;
            }
        });
    }

    $scope.create = function() {
        $scope.isCreating = true;

        requestService.post('/episode', $scope.episode, {
            success: function(response) {
                alert("등록되었습니다.");
                location.replace('/episode/list.html');
            },
            error: function(error) {
                alert(error.display_message);
            },
            then: function(response) {
                $scope.isCreating = false;
            }
        });
    }

    $scope.addGuest = function() {
        if (!$scope.episode.guest) {
            $scope.episode.guest = [""];
        } else {
            $scope.episode.guest.push("");
        }
    }

    $scope.removeGuest = function(index) {
        $scope.episode.guest.splice(index, 1);
    }

    $scope.deleteAudio = function() {
        $scope.episode.audio_id = null;
        $scope.episode.audio = null;
    }
});

app.controller('EditController', function($scope, $filter, $httpParamSerializerJQLike, requestService, cookieService) {
    $scope.dateOptions = {
        showWeeks: false,
        startDay: 1
    }

    $scope.timeOptions = {
        showMeridian: false
    }

    $scope.episode = {};

    $scope.airDateChanged = function() {
        $scope.episode.air_date = $filter('date')($scope.episode.air_date, 'yyyy-MM-dd HH:mm');
    };

    $scope.requestEpisode = function(episodeId) {
        requestService.get('/episode/' + episodeId, null, {
            success: function(response) {
                $scope.episode = response;
                $scope.airDateChanged();
            },
            error: function(error) {

            }
        });
    }

    $scope.progress = 0;

    $scope.upload = function(url) {
        $scope.isUploading = true;
        $scope.audioErrorMessage = null;

        var url = url + "?" + $httpParamSerializerJQLike({
            service: 'console',
            access_token: cookieService.get('access_token')
        });

        requestService.upload('PUT', url, {
            file: $scope.audioFile
        }, {
            success: function(audio) {
                $scope.episode.audio = audio;
                $scope.episode.audio_id = audio.id;
            },
            error: function(error) {
                alert(error.display_message);
            },
            progress: function(p) {
                if (p < 100) {
                    $scope.progress = p;
                } else {
                    $scope.progress = "데이터 확인중.."
                }
            },
            then: function(audio) {
                $scope.progress = 0;
                $scope.isUploading = false;
            }
        });
    }

    $scope.edit = function() {
        $scope.isEditing = true;

        requestService.put('/episode/' + $scope.episode.id, $scope.episode, {
            success: function(response) {
                alert("수정되었습니다.");
                location.replace('/episode/list.html');
            },
            error: function(error) {
                alert(error.display_message);
            },
            then: function(response) {
                $scope.isEditing = false;
            }
        });
    }

    $scope.deleteAudio = function() {
        if (confirm("음원을 삭제하시겠습니까? 수정완료 전까지 실제로 삭제되지 않습니다.")) {
            $scope.episode.audio = null;
        }
    }

    $scope.addGuest = function() {
        if (!$scope.episode.guest) {
            $scope.episode.guest = [""];
        } else {
            $scope.episode.guest.push("");
        }
    }

    $scope.removeGuest = function(index) {
        $scope.episode.guest.splice(index, 1);
    }

    $scope.delete = function() {
        if (confirm("정말로 삭제하시겠습니까?")) {
            requestService.delete("/episode/" + $scope.episode.id, null, {
                success: function(response) {
                    alert("삭제되었습니다.");
                    location.replace("/episode/list.html");
                },
                error: function(error) {
                    alert(error.display_message);
                }
            })
        }
    }
});
