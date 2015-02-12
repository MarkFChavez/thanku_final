(function() {
    'use strict';

    angular
        .module('thanku')
        .factory('ApiService', ApiService);

    ApiService.$inject = ['$http', '$location'];

    function ApiService($http, $location) {
        var baseUrl = "http://localhost:5000";
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
            },
            getNewsFeed: function(vm){
                // $http.get(baseUrl + "/api/v1.0/news-feed?t="+Date.now()).
                //     success(function(data) {
                //         vm.newsfeed= data.votes
                //     }).
                //     error(function(data){
                //         toastr.error(data.status + ": You failed me. . . API");
                //     });

               var promise = $http({
                  method: 'GET',
                  async: true,
                  url: baseUrl + "/api/v1.0/news-feed?t="+Date.now()
               }); 

                promise.success(function(data) {
                    vm.newsfeed= data.votes;
                }).
                error(function(data){
                    toastr.error(data.status + ": You failed me. . . API");
                });
            },
            applyVote: function(vm, points, id) {
                var params = {
                  point: points,
                  reason: vm.reason
                };
                $http.post(baseUrl + "/api/v1.0/thank/"+id, params).
                    success(function(data) {
                      if( data.status == 'ok' ) {
                        toastr.success(data.message);
                        vm.reason = "";
                      }
                    }).
                    error(function(data){
                        toastr.error(data.status + ": You failed me. . . API");
                    });
            }
        }
    }
})();
