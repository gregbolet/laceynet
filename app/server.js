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

// Now let's setup a new GameManager instance
let GameMan = new GameManager(10, 4);

// Handle a new user connection
io.on('connection', (socket) => {
	console.info(`Client connected [id=${socket.id}]`);

  // Let's add the player to the game
  GameMan.addWorker(socket);

	// Set the socket disconnect event handler
	socket.on('disconnect', () => {
		console.log('Client disconnected');
    GameMan.removeWorker(socket);
	});

  // Setup the new share request handler
  socket.on('needNewShare', (msg) => {
	  console.info(`Client needs new share [id=${socket.id}]`);

    // Get the next share for it to work on
    let shareObj = GameMan.getNewShareObjForWorker(socket);

    // If there are no shares to hand out, tell the worker to idle
    if(shareObj == null){
	    console.info(`No shares left to hand out`);
      socket.emit('idle');
    }
    else{
	    console.info(`Sending new share ${shareObj.share}`);
      socket.emit('newShare', shareObj);
    }
  });

  // Setup the completed share request handler
  // This is for shares that are not claimed to be winners
  socket.on('completedShare', (msg) => {
	  console.info(`Client completed a share [share=${msg.share} id=${socket.id}]`);
    let share = msg.share;
    let wasRejected = GameMan.reportCompletedShare(socket, share);

    if(wasRejected){
	    console.info(`share rejected`);
      socket.emit('shareRejected');
    }
    else{
	    console.info(`share accepted`);
      socket.emit('shareAccepted');
    }

  });

  socket.on('iAmAWinner', (msg) =>{
    let share = msg.share;
    let isWinningShare = GameMan.isWinningShare(share);

    if(isWinningShare){
      let wasRejected = GameMan.reportCompletedShare(socket, share);

      if(wasRejected){
        socket.emit('youDidNotWin');
        return;
      }

      // Emit to everyone EXCEPT this worker that won
      socket.broadcast.emit('weGotAWinner');

      // Let the worker know that it did in fact win
      socket.emit('youAreTheWinner');
    }
    else{
      // Just in case the share is actually a losing share
      socket.emit('youDidNotWin');
    }
  });

  // Let the client know they are registered
  socket.emit('registered');
});

// Update the page time every second
setInterval(() => {
  io.emit('time', new Date().toTimeString());
} , 1000);


