

app.controller('RadialGaugeCtrl', ['$scope', function ($scope) {
    $scope.value = -12;
    $scope.upperLimit = 5;
    $scope.lowerLimit = -23;
    $scope.unit = "dB";
    $scope.precision = 2;
    $scope.ranges = [
        {
            min: -23,
            max: -18,
            color: '#FDC702'
        },
        {
            min: -18,
            max: 0,
            color: '#8DCA2F'
        },
        {
            min: 0,
            max: 5,
            color: '#FDC702'
        }
    ];
}]);
