var app = angular.module('myApp', ['ngMaterial']);



function diffArray(inputArray, interval) {
    let result = [];

    for(let i = 0; i < inputArray.length - interval; i++) {
        result.push(inputArray[i + interval] - inputArray[i]);
    }

    return result;
}

function testVariance(array, maxVariance) {
    const differences = diffArray(array, 1);

    return differences.every(function(elt) {
        return Math.abs(elt) < maxVariance;
    });
}

class GatheredData {
    constructor() {
        this.click_results = [];
        this.answer_results = [];

        this.export = function () {
            return {
                'click': this.click_results,
                'answer': this.answer_results
            };
        };

        this.click = function (time) {
            this.click_results.push(time);
        };

        this.answer_click = function (time, id) {
            this.answer_results.push({
                'id': id,
                'time': time
            })
        }
    }
}

function GreetingController($scope, $http, $compile, $interval, $timeout, $mdDialog, $window) {
    $scope.inactiveTime = 5000;
    $scope.arhythmic = false;
    $scope.inactive = false;
    $scope.previous = [];
    $scope.rhytmVariance = 100;
    $scope.startTime = 0;
    $scope.gatheredData = new GatheredData();
    $scope.selected = [false, false, false, false];

    $scope.expData = JSON.parse(jQuery('#hidden-data').html());

    console.log($scope.expData);

    $scope.curTime = function() {
        return Math.floor(Date.now()) - $scope.startTime;
    };

    $scope.showAlert = function(message) {
        console.log("Show dialog");

        // Appending dialog to document.body to cover sidenav in docs app
        // Modal dialogs should fully cover application
        // to prevent interaction outside of dialog
        $mdDialog.show(
            $mdDialog.alert()
                .parent(angular.element(document.querySelector('#popupContainer')))
                .clickOutsideToClose(false)
                .title('Wiadomość od eksperymentatora')
                .textContent(message)
                .ariaLabel('Experiment alert')
                .ok('Dalej')
        ).finally(function() {
            console.log("Closed the alert dialog");
            $scope.startTime = $scope.curTime();

            if($scope.expData.executionTime !== 0) {
                $timeout($scope.sendUpdate, $scope.expData.executionTime);
            }

        });
    };

    $scope.clicked = function() {
        const time = $scope.curTime();

        $scope.previous.push(time);
        $scope.gatheredData.click(time);
        $scope.checkRhythmic();
    };

    $scope.isRhythmicFor = function (interval) {
        const intervalsDiffs = diffArray($scope.previous, interval);
        const result = testVariance(intervalsDiffs, $scope.rhytmVariance);

        if(result) {
            console.log("Rhytmic for inteval size: " + interval);
        }

        return result;
    };

    $scope.checkRhythmic = function () {
        // TODO Algorytm kontroli rytmiczności wykonywania zadania GIL
        // console.log($scope.previous);

        const compTime = $scope.curTime();

        $scope.previous = $scope.previous.filter(function(elt) {
            return elt + $scope.inactiveTime >= compTime;
        });

        if($scope.previous.length === 0) {
            $scope.inactive = true;
        } else {
            $scope.inactive = false;
            $scope.arhythmic = false;
            if($scope.previous.length > 3) {
                $scope.arhythmic = true;
                for(let intervalSize = 1; intervalSize < $scope.previous.length - 3; intervalSize++) {
                    $scope.arhythmic = $scope.arhythmic && (!$scope.isRhythmicFor(intervalSize));
                }
            }
        }
    };

    $scope.clickedAnswer = function(item) {
        $scope.selected[item] = !$scope.selected[item];
        $scope.gatheredData.answer_click($scope.curTime(), item);
    };

    $interval(function(){
      $scope.checkRhythmic();
    }, 300, false);

    if($scope.expData.showAlert) {
        $scope.showAlert($scope.expData.startMessage);
    } else {
        $scope.startTime = $scope.curTime();
    }

    $scope.sendUpdate = function () {
        const url = document.location.pathname + $scope.expData.stage;

        console.log("Sending to url: " + url);

        $http.put(url, $scope.gatheredData.export())
            .success(function() {
                console.log("Managed to send the request");
                $window.location.reload();
            })
            .error(function() {
                console.log("Failed to send the request");
            })
    };

    $scope.clickNext = function() {
        console.log("Clicking next");

        const url = document.location.pathname + "next";

        $http.post(url, {})
            .success(function() {
                console.log("Managed to send the request");
                $scope.sendUpdate();
            })
            .error(function() {
                console.log("Failed to click next")
            })

    };
}

GreetingController.$inject = ['$scope', '$http', '$compile', '$interval', '$timeout', '$mdDialog', '$window'];

app.controller("GreetingController", GreetingController);

