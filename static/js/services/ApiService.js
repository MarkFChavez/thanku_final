(function() {
    'use strict';

    angular
        .module('thanku')
        .factory('ApiService', ApiService);

    ApiService.$inject = ['$http', '$location'];

    function ApiService($http, $location) {
        var baseUrl = "http://fa390c1.ngrok.com";
        return {
            login: function(vm) {
                $.ajax({
                    type: "POST",
                    url: baseUrl + "/api/v1.0/signin",
                    dataType: "json",
                    data: {
                        username: vm.username,
                        password: vm.password
                    },
                    success: function (data) {
                        if (data.status == "ok") {
                            toastr.success("Welcome! " + data.user.first_name);
                            setTimeout(function(){ window.location.href = '/#/dashboard'; },1500);
                        } else {
                            toastr.error(data.message)
                        }
                    },
                    error: function (data) {
                        toastr.error(data.status + ": You failed me. . .");
                    }
                });
            },
            getUserList: function(vm){
                $http.get(baseUrl + "/api/v1.0/users").
                    success(function(data) {
                        vm.users = data.users;
                    }).
                    error(function(data){
                        toastr.error(data.status + ": You failed me. . . API");
                    });
            }
        }
    }
})();
