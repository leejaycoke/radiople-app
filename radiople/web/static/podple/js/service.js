app.service('requestService', function($http, Upload, $httpParamSerializerJQLike) {
    var options = {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    }

    this.get = function(url, params, callbacks) {
        if (params) {
            url += '?' + $httpParamSerializerJQLike(params);
        }
        $http.get(url).
        success(function(data, status, headers) {
            if ('success' in callbacks) {
                callbacks.success(data);
            }
        }).
        error(function(data, status, headers) {
            if ('error' in callbacks) {
                if (data) {
                    callbacks.error(data.display_message);
                }
                else {
                    callbacks.error("네트워크 연결에 실패했습니다.");
                }
            }
        }).
        then(function(data, status, headers) {
            if ('then' in callbacks) {
                callbacks.then(data);
            }
        });
    };

    this.put = function(url, data, callbacks) {
        $http.put(url, $httpParamSerializerJQLike(data), options).
        success(function(data, status, headers) {
            if ('success' in callbacks) {
                callbacks.success(data);
            }
        }).
        error(function(data, status, headers) {
            if ('error' in callbacks) {
                if (data) {
                    callbacks.error(data.display_message);
                }
                else {
                    callbacks.error("네트워크 연결에 실패했습니다.");
                }
            }
        }).
        then(function(data, status, headers) {
            if ('then' in callbacks) {
                callbacks.then(data);
            }
        });
    };

    this.post = function(url, data, callbacks) {
        $http.post(url, $httpParamSerializerJQLike(data), options).
        success(function(data, status, headers) {
            if ('success' in callbacks) {
                callbacks.success(data);
            }
        }).
        error(function(data, status, headers) {
            console.log(data)
            if ('error' in callbacks) {
                if (data) {
                    callbacks.error(data.display_message);
                }
                else {
                    callbacks.error("네트워크 연결에 실패했습니다.");
                }
            }
        }).
        then(function(data, status, headers) {
            if ('then' in callbacks) {
                callbacks.then(data);
            }
        });
    };

    this.delete = function(url, data, callbacks) {
        $http.delete(url, $httpParamSerializerJQLike(data), options).
        success(function(data, status, headers) {
            if ('success' in callbacks) {
                callbacks.success(data);
            }
        }).
        error(function(data, status, headers) {
            console.log(data)
            if ('error' in callbacks) {
                if (data) {
                    callbacks.error(data.display_message);
                }
                else {
                    callbacks.error("네트워크 연결에 실패했습니다.");
                }
            }
        }).
        then(function(data, status, headers) {
            if ('then' in callbacks) {
                callbacks.then(data);
            }
        });
    };

    this.upload = function(method, url, data, callbacks) {
        Upload.upload({
            url: url,
            method: method,
            data: data,
            disableProgress: !('progress' in callbacks)
        }).success(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response);
            }
            if ('then' in callbacks) {
                callbacks.then(response);
            }
        }).error(function(error) {
            if ('error' in callbacks) {
                if (error) {
                    callbacks.error(error)
                }
                else {
                    callbacks.error("네트워크 연결에 실패했습니다.");
                }
            }
            if ('then' in callbacks) {
                callbacks.then(error);
            }
        }).progress(function(e) {
            if ('progress' in callbacks) {
                callbacks.progress(parseInt(100.0 * e.loaded / e.total));
            }
        });
    };

});
