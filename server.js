const {SlowBuffer} = require("buffer");
const {readdirSync} = require("fs");
const http = require("http");
const internal = require("stream");
const fs = require("fs").promises;
const host = "localhost";
const port = 8000;

var players = {}; //stores data of all the players based on connection ID strings
const server = http.createServer((req, res) => {
    switch (req.url) {
        case "/Connect":
            res.writeHead(200);
            newConnectId = Object.keys(players).length.toString();
            playersSortedInts = [];
            for (var i = 0; i < Object.keys(players).length; i++) {
                var j;
                for (j = 0; j < playersSortedInts.length; j++) { if (parseInt(Object.keys(players)[i]) < playersSortedInts[j]) { break; } }
                playersSortedInts.splice(j, 0, parseInt(Object.keys(players)[i]));
            }
            for (var l = 0; l < playersSortedInts.length - 1; l++) {
                if (playersSortedInts[l + 1] - playersSortedInts[l] > 1) {
                    newConnectId = (l + 1).toString();
                    break;
                }
            }
            players[newConnectId] = {
                "x": 50,
                "y": 300,
                "xvel": 0,
                "yvel": 0,
                "in_air": true
            }
            res.end(JSON.stringify([newConnectId]));
            break;
        case "/ServerPost":
            res.setHeader("Content-Type", "application/json");
            res.writeHead(200);
            req.on("data", chunk => {
                console.log(`Chunk Received: ${chunk}`);
                chunk = JSON.parse(chunk);
                chunkIndex = chunk["connectionId"];
                delete chunk["connectionId"];
                chunk["seconds_played"] = Math.round(chunk["seconds_played"]);
                players[chunkIndex] = chunk;
                console.log(chunk);
            });
            console.log(JSON.stringify(players));
            res.end(JSON.stringify(players));
            break;
        case "/Quit":
            res.writeHead(200);
            req.on("data", chunk => {
                chunk = JSON.parse(chunk);
                console.log(`Player Quit: ${chunk[0]}`);
                delete players[chunk[0]];
            });
            res.end(JSON.stringify({ "Completed": true }));
            break;
        default:
            res.setHeader("Content-Type", "application/json");
            res.writeHead(404);
            res.end(JSON.stringify({ "Error": "Resource not found" }));
    }
})

server.listen(port, host, () => {
    console.log(`Server running at http://${host}:${port}`);
});