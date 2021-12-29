const express = require('express');
//const WebSocket = require('ws');
const socketIO = require('socket.io');

const PORT = process.env.PORT || 5000;
const app = express();

// Serve all the files from the /public folder
// Given public/index.html it will be served from myaddress.com/index.html
app.use(express.static('public'))

const server = app.listen(PORT, function() {
  console.log(`Example app listening on port ${PORT}!`)
});

// socketIO will server the websockets and handle reverse
// compatibility and fallback
const io = socketIO(server);

io.on('connection', (socket) => {
    console.log('Client connected');
    socket.on('disconnect', () => console.log('Client disconnected'));
});

// Update the page time every second
setInterval(() => {
  io.emit('time', new Date().toTimeString());
} , 1000);


//// Set up a websocket server
//const wss = new WebSocket.Server({ server });
//
//// Handle the incoming websocket connection
//wss.on('connection', socket => {
//  console.log('Client connected!');
//  socket.on('message', message => console.log(message));
//  socket.on('close', () => console.log('Client disconnected'));
//});

// Update the time each second on the client
//setInterval(() => {
//    wss.clients.forEach((client) => {
//          client.send(new Date().toTimeString());
//        });
//}, 1000);

