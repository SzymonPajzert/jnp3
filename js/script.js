var app = angular.module('myApp', []);

app.directive('shortcut', function() {
  return {
    restrict: 'E',
    replace: true,
    scope: true,
    link: function postLink(scope, iElement, iAttrs){
      $(document)
        .on('keypressed', function(e){scope.$apply(scope.keyDown(e));})
        .on('keyup', function(e){scope.$apply(scope.keyUp(e));});
    }
  };
});

function GreetingController($scope, $document) {
  log("hehe");

  $scope.pressed = [false, false, false, false, false, false];

  $scope.keyDown = function(event) {
    var key = toInt(event);
    if(key != null) {
      $scope.pressed[key] = true;
    }
    console.log($scope.pressed);
  };

  $scope.keyUp = function(event) {
    var key = toInt(event);
    if(key != null) {
      $scope.pressed[key] = false;
    }
  };

  $scope.ask = function(item) {
    return $scope.pressed[item];
  };

  $(document)
    .bind('keydown', function(e){$scope.$apply($scope.keyDown(e));})
    .bind('keyup', function(e){$scope.$apply($scope.keyUp(e));});
};

GreetingController.$inject = ['$scope'];

app.controller("GreetingController", GreetingController);

function toInt(event) {
  if(!isNaN(event.key)) {
    if(event.key == "0") {
      return parseInt(event.key) + 9;
    } else {
      return parseInt(event.key) - 1;
    }
  } else {
    return null;
  }
}

