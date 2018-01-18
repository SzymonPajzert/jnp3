function toInt(event) {
    if (!isNaN(event.key)) {
        return fromKey(parseInt(event.key));
    } else {
        return null;
    }
}

function fromKey(value) {
    if (value === 0) {
        return 9;
    } else {
        return value - 1;
    }
}

function toKey(value) {
    if (value === 9) {
        return 0;
    } else {
        return value + 1;
    }
}
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
        }
    };
});

function GreetingController($scope, $http, $compile) {
    console.log("hehe");

    $scope.prevTime = Date.now();

    $scope.checkState = function () {
        console.log("Checking log");

        const reducer = function (accumulator, current) {
            return accumulator && (!current);
        };

        if($scope.light.reduce(reducer, true)) {
            console.log("Creating new");

            var timeNow = Date.now();
            $scope.getData(timeNow - $scope.prevTime);
            $scope.prevTime = timeNow;
        }
    };

    $scope.keyDown = function (event) {
        var key = toInt(event);
        if (key != null) {
            if(!$scope.light[key]) {
                $(".my_audio").trigger('load');
                $(".my_audio").trigger('play');
            }

            $scope.light[key] = false;
        }

        $scope.checkState();
    };

    $scope.ask = function (item) {
        return $scope.light[item];
    };

    $(document)
        .bind('keydown', function (e) {
            $scope.$apply($scope.keyDown(e));
        });

    $scope.checkState();

    $http
        .get(window.location + '/config')
        .success(function (results) {
            console.log(results);
            $scope.delay = results.delay;
            $scope.feedback = results.feedback;
        })
        .error(function (error) {
            console.log(error);
        });


    $scope.getData = function (time) {
        var data = {
            time: time
        };
        console.log(data)

        $http
            .post(window.location + '/data/new', data)
            .success(function (results) {
                console.log(results);
                $scope.light = results;
            })
            .error(function (error) {
                console.log(error);
            });
    };

    $scope.getData(0); // we don't have anything set yet, so we don't have to care

    const indexRange = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

    indexRange.forEach(function (item) {
        var item_id="lamp" +  item;
        var item_class="lamp ";

        if ($scope.ask(item)) {
            item_class = item_class + "light";
        } else {
            item_class = item_class + "dark";
        }

        var item_ng_class=`{light: ask(${item}), dark: !ask(${item})}`;

        var newEle = angular.element(
            "<div id=\"" + item_id + "\" class=\"" +
            item_class + "\" ng-class=\"" + item_ng_class + "\">" +
            toKey(item) + "</div>");
        $compile(newEle)($scope);

        var target = document.getElementById('row');
        angular.element(target).append(newEle);
    });


    console.log("Done");
}

GreetingController.$inject = ['$scope', '$http', '$compile'];

app.controller("GreetingController", GreetingController);

