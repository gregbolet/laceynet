const express = require('express');
//const WebSocket = require('ws');
const socketIO = require('socket.io');
const GameManager = require('./gameManager.js');

const PORT = process.env.PORT || 5000;
const app = express();

// Serve all the files from the /public folder
// Given public/index.html it will be served from myaddress.com/index.html
app.use(express.static('public'))

const server = app.listen(PORT, function() {
	console.log(`Game Server UI listening on port ${PORT}!`)
});

// socketIO will serve the websockets and handle reverse
// compatibility and fallback
const io = socketIO(server);

// Now let's setup a new gameManager instance
let GameMan = new GameManager(10, 1);


// Handle a new user connection
io.on('connection', (socket) => {
	console.info(`Client connected [id=${socket.id}]`);

	// Set the socket disconnect event handler
	socket.on('disconnect', () => {
		console.log('Client disconnected');
		clients.delete(socket);
	});

  // Setup the new share request handler
  socket.on('getNewShare', (msg) => {

    socket.emit('newShare', {share:[0,1,2,3], winningNum:2});
  });

  // Setup the completed share request handler
  socket.on('reportCompleted', (msg) => {

  });

  // Let the client know they are registered
  socket.emit('registered');
});

// Update the page time every second
setInterval(() => {
	io.emit('time', new Date().toTimeString());
} , 1000);


