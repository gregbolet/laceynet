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

// socketIO will serve the websockets and handle reverse
// compatibility and fallback
const io = socketIO(server);

// This will map socketIDs (i.e: clients) to their assigned game numbers
let clients = new Map();

io.on('connection', (socket) => {
  console.info(`Client connected [id=${socket.id}]`);

  // Add the client to the client list, keep their game info
  clients.set(socket, {nums: [], currIdx: -1});

  socket.on('disconnect', () => {
	  console.log('Client disconnected');
	  clients.delete(socket);
  });

  socket.on('clicked', (msg) => {
	console.log(`playerid ${socket.id}, msg: `, msg);	
  });

});

// Update the page time every second
setInterval(() => {
  io.emit('time', new Date().toTimeString());
} , 1000);


