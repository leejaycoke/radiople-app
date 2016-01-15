app.service('cookieService', function($cookies) {
    this.get = function(key) {
        var value = $cookies.get(key);
        if (value) {
            return value.trim().replace(/"/g, '');
        }
        return null;
    }
});

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
        then(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response.data);
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(error) {
            if ('error' in callbacks) {
                if (error != null && error.data != null) {
                    callbacks.error(error.data);
                } else {
                    callbacks.error({
                        display_message: "네트워크 연결에 실패했습니다."
                    });
                }
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        });
    };

    this.put = function(url, data, callbacks) {
        $http.put(url, $httpParamSerializerJQLike(data), options).
        then(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response.data);
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(error) {
            if ('error' in callbacks) {
                if (error != null && error.data != null) {
                    callbacks.error(error.data);
                } else {
                    callbacks.error({
                        display_message: "네트워크 연결에 실패했습니다."
                    });
                }
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        });
    };

    this.post = function(url, data, callbacks) {
        $http.post(url, $httpParamSerializerJQLike(data), options).
        then(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response.data);
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(error) {
            if ('error' in callbacks) {
                if (error != null && error.data != null) {
                    callbacks.error(error.data);
                } else {
                    callbacks.error({
                        display_message: "네트워크 연결에 실패했습니다."
                    });
                }
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        });
    };

    this.postJson = function(url, data, callbacks) {
        $http.post(url, data, options).
        then(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response.data);
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(error) {
            if ('error' in callbacks) {
                if (error != null && error.data != null) {
                    callbacks.error(error.data);
                } else {
                    callbacks.error({
                        display_message: "네트워크 연결에 실패했습니다."
                    });
                }
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        });
    };

    this.delete = function(url, data, callbacks) {
        $http.delete(url, $httpParamSerializerJQLike(data), options).
        then(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response.data);
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(error) {
            if ('error' in callbacks) {
                if (error != null && error.data != null) {
                    callbacks.error(error.data);
                } else {
                    callbacks.error({
                        display_message: "네트워크 연결에 실패했습니다."
                    });
                }
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        });
    };

    this.upload = function(method, url, data, callbacks) {
        Upload.upload({
            url: url,
            method: method,
            data: data,
            disableProgress: !('progress' in callbacks)
        }).then(function(response) {
            if ('success' in callbacks) {
                callbacks.success(response.data);
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(error) {
            if ('error' in callbacks) {
                if (error != null && error.data != null) {
                    callbacks.error(error.data);
                } else {
                    callbacks.error({
                        display_message: "네트워크 연결에 실패했습니다."
                    });
                }
            }
            if ('then' in callbacks) {
                callbacks.then();
            }
        }, function(e) {
            callbacks.progress(parseInt(100.0 * e.loaded / e.total));
        });
    }
});
