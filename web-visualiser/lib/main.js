/**
 * Created by regis on 20.10.2016.
 */

function SettingsPanel(settingsPanelId, visualiser) {
    var data = visualiser.getData();
    var settingsPanel = $(settingsPanelId);

    var _toggleList = function () {
        var listId = parseInt($(this).attr("data-id"));
        var currentLists = visualiser.getShowingList();
        var currentPosition = currentLists.indexOf(listId);
        var state = $(this).is(':checked');
        if (state) {
            if (currentPosition == -1) {
                currentLists.push(listId);
            }
        } else {
            if (currentPosition != -1) {
                currentLists.splice(currentPosition, 1);
            }
        }
        visualiser.setShowingLists(currentLists);
    }

    var _initListsPanel = function () {
        var lists = data.users[0].lists;
        var templateList = settingsPanel.find(".listCheckbox.template");
        for (var listIndex in lists) {
            var listBlock = templateList.clone();
            listBlock.removeClass("template");
            listBlock.find(".listTitle").text("List #" + lists[listIndex].id);
            listBlock.find("input").attr("data-id", lists[listIndex].id).change(_toggleList);
            settingsPanel.find(".lists").append(listBlock);
        }
    };

    var _initSettingsPanel = function () {
        settingsPanel.find("input[name='showInterclusterConnections']").change(function () {
            visualiser.setShowingInterclusterConnections($(this).is(':checked'));
        });

        settingsPanel.find("input[name='showNames']").change(function () {
            visualiser.setShowingNames($(this).is(':checked'));
        });

        settingsPanel.find("input[name='showDesires']").change(function () {
            visualiser.setShowingDesires($(this).is(':checked'));
        });
        _initListsPanel();
    };

    _initSettingsPanel();
}

function TeamsPanel(panelId, visualiser) {
    var panel = $(panelId);
    var _metricsPrecision = 2;
    var data = visualiser.getData();
    var _createAddTeamBlock = function (team) {
        console.log(team.metric);
        var template = panel.find(".template.teamBlock");
        var teamBlock = template.clone();
        teamBlock.find(".panel-title").text("Cluster #" + team.id);
        teamBlock.find(".panel-heading").css("background", team.color);
        teamBlock.removeClass("template");
        var metricsBlock = teamBlock.find(".metrics");
        metricsBlock.empty();

        var finalMetric = team.metric.finalMetric;
        if (finalMetric) {
            var finalMetricBlock = template.find(".finalMetric").clone();
            finalMetricBlock.find(".finalValue").text("Fin " + finalMetric.toFixed(_metricsPrecision));
            metricsBlock.append(finalMetricBlock);
        }

        var desiresMetric = team.metric.desiresMetric;
        if (desiresMetric) {
            var desiresMetricBlock = template.find(".desiresMetric").clone();
            desiresMetricBlock.find(".finalValue").text("Fin " + desiresMetric.value.toFixed(_metricsPrecision));
            metricsBlock.append(desiresMetricBlock);
        }

        for (var listIndex in team.metric.listsMetrics) {
            var metric = team.metric.listsMetrics[listIndex];
            var listMetricBlock = template.find(".listMetric").clone();
            listMetricBlock.find(".metricName").text("List " + metric.id);
            listMetricBlock.find(".finalValue").text("Fin " + metric.final.toFixed(_metricsPrecision));
            listMetricBlock.find(".averageValue").text("Avg " + metric.average.toFixed(_metricsPrecision));
            listMetricBlock.find(".thresholdValue").text("Thr " + metric.threshold.toFixed(_metricsPrecision));
            metricsBlock.append(listMetricBlock);
        }

        for (var userIdIndex in team.user_ids) {
            var userId = team.user_ids[userIdIndex];
        }
        panel.children(".panel-body").append(teamBlock);
    }

    for (var clusterKey in data.clusters) {
        _createAddTeamBlock(data.clusters[clusterKey]);
    }
}

function Vizualizer(canvasId, data) {

    var canvas = $(canvasId);


    var teamColors = ["#ff8000", "#0040ff", "#00FF00", "#800000", "#008080", "#FFD700"];
    var edgeColors = ["#72DCF0", "#8BEC78", "#075A9F", "#A7FD2D", "#7EB8DC"];
    var negativeThreshold = -0.3
    var significantThreshold = 0.5;
    var showNotSignificant = false;
    var listsToShow = [];
    var showDesires = false;
    var showNames = false;
    var showInterClusterConnections = false;
    var sys;


    var _addUsers = function () {
        for (var userKey in data.users) {
            var user = data.users[userKey];
            //user.name = "Имя Фамильевич";
            //console.log("Adding "+user.id)
            sys.addNode(user.id, user);
        }
    }

    var _generateEdges = function () {
        for (var i = 0; i < data.users.length; i++) {
            for (var j = i + 1; j < data.users.length; j++) {
                _generateDesiresEdge(data.users[i], data.users[j]);
            }
        }
        _generateListsEdges();
    }

    var _addEdge = function (user1, user2, data) {
        if (_checkEdge(user1, user2, data)) {
            var userWithMinId = Math.min(user1, user2);
            var userWithMaxId = Math.max(user1, user2);
            var edges = sys.getEdges(userWithMinId, userWithMaxId);
            if (edges.length == 0) {
                sys.addEdge(userWithMinId, userWithMaxId, {"edges": []});
                edges = sys.getEdges(userWithMinId, userWithMaxId);
            }
            edges[0].data.edges.push(data);
        }
    }


    var _checkEdge = function (user1Id, user2Id, data) {
        var user1 = _getUserById(user1Id);
        var user2 = _getUserById(user2Id);
        if (!showInterClusterConnections && user1.cluster_id != user2.cluster_id) {
            return false;
        }
        if (data.type == "list" && listsToShow.indexOf(data.listId) == -1) {
            return false;
        }
        else if (data.type == "desire" && !showDesires) {
            return false;
        }

        return true;
    }

    var _refreshEdges = function () {
        sys.eachEdge(function (e) {
            sys.pruneEdge(e);
        })
        _generateEdges();
    }

    var _generateDesiresEdge = function (user1, user2) {
        var secondWasSelectedByFirst = user1.selectedPeople.indexOf(user2.id) != -1;
        var firstWasSelectedBySecond = user2.selectedPeople.indexOf(user1.id) != -1;
        if (secondWasSelectedByFirst && firstWasSelectedBySecond) {
            _addEdge(user1.id, user2.id, {"type": "desire", "isMutual": true});
        } else if (secondWasSelectedByFirst) {
            _addEdge(user1.id, user2.id, {"type": "desire", "isMutual": false});
        } else if (firstWasSelectedBySecond) {
            _addEdge(user2.id, user1.id, {"type": "desire", "isMutual": false});
        }
    }

    var _isSignificant = function (distance) {
        return distance < negativeThreshold || distance > significantThreshold;
    }

    var _generateListsEdges = function () {
        for (var pairIndex in data.pairDistances) {
            var pair = data.pairDistances[pairIndex];
            for (var listIndex in pair.distances) {
                var listDistance = pair.distances[listIndex];
                if (showNotSignificant || _isSignificant(listDistance.distance)) {
                    _addEdge(pair.user1, pair.user2, {
                        "type": "list",
                        "listId": listDistance.id,
                        "distance": listDistance.distance
                    });
                }

            }
        }
    }

    var _getUserById = function (id) {
        for (var userIndex in data.users) {
            var user = data.users[userIndex];
            if (user.id == id) {
                return user;
            }
        }
    }

    var _colorizeTeams = function () {
        for (var teamKey in data.clusters) {
            var team = data.clusters[teamKey];
            team.color = teamColors.pop();
            for (var teamMemberIndex in team.users_ids) {
                var teamMemberId = team.users_ids[teamMemberIndex];
                var user = _getUserById(teamMemberId);
                user.color = team.color;
                user.cluster_id = team.id;
            }
        }
    }

    var that = {
        init: function () {
            sys = arbor.ParticleSystem(); // создаём систему
            sys.renderer = Renderer(canvas.get(0), that);
            sys.parameters({gravity: true, repulsion: 2000, stiffness: 100}); // гравитация вкл
            sys.screenSize(canvas.width(), canvas.height());
            //console.log(canvas.width, canvas.height);
            sys.screenPadding(50);
            _addUsers();
            _colorizeTeams();
            _generateEdges();
            sys.renderer.initMouseHandling();

        },
        getSys: function () {
            return sys;
        },
        getEdgeColorFor: function (listId) {
            return edgeColors[listId];
        },
        getNegativeThreshold: function () {
            return negativeThreshold
        },
        setShowingLists: function (listsIds) {
            listsToShow = listsIds;
            _refreshEdges();
        },
        setShowingDesires: function (shouldShow) {
            showDesires = shouldShow;
            _refreshEdges();
        },
        setShowingInterclusterConnections: function (shouldShow) {
            showInterClusterConnections = shouldShow;
            _refreshEdges();
        },
        setShowingNames: function (shouldShow) {
            showNames = shouldShow;
            sys.renderer.redraw();
        },
        getShowingList: function () {
            return listsToShow.slice();
        },
        getShowingNames: function () {
            return showNames;
        },
        getData: function () {
            return data;
        }
    };
    return that;
}


function Renderer(canvas, visualizer) {
    var system;
    var ctx = canvas.getContext('2d');
    var edgeBaseWidth = 10;
    var nodeWidth = 100;
    var nodeHeight = 70;
    var bezierBase = 50;

    var _findSuitableFontSize = function (textParts, width) {
        var actualWidth;
        var fontSize = 30;
        do {
            fontSize--;
            ctx.font = fontSize + 'px sans-serif';
            actualWidth = 0;
            for (var part in textParts) {
                var widthInfo = ctx.measureText(textParts[part]);
                if (widthInfo.width > actualWidth) {
                    actualWidth = widthInfo.width;
                }
            }
        }
        while (actualWidth > width);
        return fontSize;
    }

    var _drawNode = function (node, pt) {
        var label = node.data.name && visualizer.getShowingNames() ? node.data.name : String(node.data.id);

        var topX = pt.x - nodeWidth / 2;
        var topY = pt.y - nodeHeight / 2;

        ctx.fillStyle = node.data.color;
        ctx.fillRect(topX, topY, nodeWidth, nodeHeight);

        var textParts = label.split(" ");
        var fontSize = _findSuitableFontSize(textParts, nodeWidth - 10);
        ctx.font = fontSize + 'px sans-serif';
        ctx.fillStyle = "black";
        y = 5;
        for (var part in textParts) {
            y += fontSize;
            ctx.fillText(textParts[part], topX + 5, topY + y);

        }

    };

    var _drawEdge = function (edge, pt1, pt2) {
        var bezierOffset = 0;
        for (var subEdgeIndex in edge.data.edges) {
            var subEdge = edge.data.edges[subEdgeIndex];
            var relativeWidth = 0;
            var color = "black";
            var isDashed = false;
            var defined = false;

            //console.log(subEdge)
            if (subEdge.type == "desire") {
                if (subEdge.isMutual) {
                    relativeWidth = 1;
                } else {
                    relativeWidth = 0.5;
                }
                defined = true;
                color = visualizer.getEdgeColorFor(0);
            }
            else if (subEdge.type == "list") {
                relativeWidth = Math.abs(subEdge.distance);
                defined = true;
                if (subEdge.distance < visualizer.getNegativeThreshold()) {
                    isDashed = true;
                }
                color = color = visualizer.getEdgeColorFor(subEdge.listId + 1);
            }
            var absoluteWidth = edgeBaseWidth * relativeWidth;
            if (defined)
                _drawLine(pt1, pt2, bezierOffset, absoluteWidth, isDashed, color);
            bezierOffset = (bezierOffset < 0) ? bezierOffset * (-1) : Math.abs(bezierOffset) + bezierBase;
        }

    }

    var _drawLine = function (pt1, pt2, bezierOffset, width, isDashed, color) {
        ctx.beginPath();
        ctx.moveTo(pt1.x, pt1.y);
        if (isDashed) {
            ctx.setLineDash([30, 5]);
        } else {
            ctx.setLineDash([0]);
        }
        ctx.lineWidth = width;
        ctx.strokeStyle = color;
        ctx.bezierCurveTo(pt1.x, pt1.y + bezierOffset, pt2.x, pt2.y + bezierOffset, pt2.x, pt2.y);
        ctx.stroke();
    }

    var that = {
        init: function (_system) {
            console.log("init");
            system = _system;
        },
        redraw: function () {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            system.eachEdge(_drawEdge);
            system.eachNode(_drawNode);

        },
        initMouseHandling: function () {
            var dragged = null;
            var handler = {
                clicked: function (e) {
                    var pos = $(canvas).offset();
                    _mouseP = arbor.Point(e.pageX - pos.left, e.pageY - pos.top);
                    dragged = system.nearest(_mouseP);
                    if (dragged && dragged.node !== null) {
                        dragged.node.fixed = true;
                    }
                    $(canvas).bind('mousemove', handler.dragged);
                    $(window).bind('mouseup', handler.dropped);
                    return false;
                },
                dragged: function (e) {
                    var pos = $(canvas).offset();
                    var s = arbor.Point(e.pageX - pos.left, e.pageY - pos.top);

                    if (dragged && dragged.node !== null) {
                        var p = system.fromScreen(s);
                        dragged.node.p = p;
                    }

                    return false;
                },
                dropped: function (e) {
                    if (dragged === null || dragged.node === undefined) return;
                    if (dragged.node !== null) dragged.node.fixed = false;
                    dragged = null;
                    $(canvas).unbind('mousemove', handler.dragged);
                    $(window).unbind('mouseup', handler.dropped);
                    _mouseP = null;
                    return false;
                }
            }
            $(canvas).mousedown(handler.clicked);
        }
    }
    return that;
}


//Canvas resizer
(function () {
    $(function () {
        var canvas = $('#viewport');//, context = canvas.getContext('2d');
        var teamsPanel = $('#teamsPanel');

        function resizeCanvas() {
            console.log("resize");
            window.addEventListener('resize', resizeCanvas, false);
            canvas.get(0).width = canvas.parent().width();
            canvas.get(0).height = window.innerHeight;
            var plusHeight = window.innerHeight - (teamsPanel.position().top + teamsPanel.outerHeight());
            teamsPanel.children(".panel-body").height(teamsPanel.height() + plusHeight - 100);
            console.log();
        }

        resizeCanvas();
    });
})();