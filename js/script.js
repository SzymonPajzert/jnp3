var app = angular.module('myApp', []);

app.directive('shortcut', function () {
    return {
        restrict: 'E',
        replace: true,
        scope: true,
        link: function postLink(scope, iElement, iAttrs) {
            $(document)
                .on('keypressed', function (e) {
                    scope.$apply(scope.keyDown(e));
                })
                .on('keyup', function (e) {
                    scope.$apply(scope.keyUp(e));
                });
        }
    };
});

function GreetingController($scope, $http) {
    console.log("hehe");

    $scope.pressed = [false, false, false, false, false, false];

    $scope.keyDown = function (event) {
        var key = toInt(event);
        if (key != null) {
            $scope.pressed[key] = true;
        }

        console.log('hifhidfi');
        var file = new Audio(window.location.href + 'static/Buzz-SoundBible.com-1790490578.mp3');
        file.play();
    };

    $scope.keyUp = function (event) {
        var key = toInt(event);
        if (key != null) {
            $scope.pressed[key] = false;
        }
    };

    $scope.ask = function (item) {
        return $scope.pressed[item];
    };

    $(document)
        .bind('keydown', function (e) {
            $scope.$apply($scope.keyDown(e));
        })
        .bind('keyup', function (e) {
            $scope.$apply($scope.keyUp(e));
        });

    $http.get(window.location + '/config').success(function (results) {
        console.log(results);
        $scope.delay = results.delay;
        $scope.feedback = results.feedback;
    }).error(function (error) {
        console.log(error);
    });


}

GreetingController.$inject = ['$scope', '$http'];

app.controller("GreetingController", GreetingController);

function toInt(event) {
    if (!isNaN(event.key)) {
        if (event.key == "0") {
            return parseInt(event.key) + 9;
        } else {
            return parseInt(event.key) - 1;
        }
    } else {
        return null;
    }
}

