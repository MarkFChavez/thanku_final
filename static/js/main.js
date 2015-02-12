(function() {
  'use strict';

  angular.module('thanku', [
    'ngRoute'
  ])
      .config(['$routeProvider', '$locationProvider', '$interpolateProvider', function($routeProvider, $locationProvider, $interpolateProvider) {

        $interpolateProvider.startSymbol("{[{").endSymbol("}]}");

        $routeProvider
            .when('/', {
              templateUrl: 'login.html',
              controller: 'LoginController',
              controllerAs: 'vm'
            })
            .when('/dashboard', {
              templateUrl: 'dashboard.html',
              controller: 'DashboardController',
              controllerAs: 'vm'
            })
            .otherwise({
              template: '<h1>Error 404</h1>'
            });


      }]);
})();
