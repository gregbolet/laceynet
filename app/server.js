const express = require('express');
//const WebSocket = require('ws');
const socketIO = require('socket.io');
const GameManager = require('./gameManager.js');

const PORT = process.env.PORT || 5000;
const app = express();

// Serve all the files from the /public folder
// Given public/index.html it will be served from myaddress.com/index.html
app.use(express.static('public'))

const server = app.listen(PORT, function () {
  console.log(`Game Server UI listening on port ${PORT}!`)
});

// socketIO will serve the websockets and handle reverse
// compatibility and protocol fallback
const io = socketIO(server);

// Now let's setup a new GameManager instance
let GameMan = new GameManager(10, 4);

// Keep track of whether we need to restart the game
let gameOver = false;

let numberDict = {}; //dictionary of client ids and their guesses

let clientDict = new Map();

const adminIo = io.of('/admin.html');

const clientIo = io.of('/');

//admin client namespace
adminIo.on('connection', (socket) => {
  console.info(`Admin Client connected [id=${socket.id}]`);
 
  socket.on('disconnect', () => {
    console.log('Admin Client disconnected');
    
  });

  socket.on('refreshPress', (msg) => { //kind of useless now?
    let transitString = JSON.stringify(Array.from(clientDict));
    adminIo.emit('numberSwitch',transitString);
  });

  // Handle a request to restart the game
  socket.on('restartGame', (msg) => {
    console.log(`Restarting game with current workers!`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    clientDict = new Map();
    // Tell all the players we restarted
    adminIo.emit('restartGame');
    io.emit('restartGame');
  });

  socket.on('getParams', (msg) => {
    
  })

  socket.on('setNewGameParams', (msg) =>{
    console.log('Changing the game parameters');
    GameMan.resetGameParameters(msg);
    console.info(`Restarting game with current workers! - ADMIN`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;

    // Tell all the players we restarted
    io.emit('restartGame');
    adminIo.emit('restartGame');
  });
  let transitString = JSON.stringify(Array.from(clientDict));
  socket.emit('registered',transitString); //when admin is added, pass client dictionary and populate screen

});
// Handle a new user connection
clientIo.on('connection', (socket) => {
  console.info(`Client connected [id=${socket.id}]`);
  // Let's add the player to the game
  GameMan.addWorker(socket);
 
  // Set the socket disconnect event handler
  socket.on('disconnect', () => {
    console.log('Client disconnected');
    GameMan.removeWorker(socket);
    clientDict.delete(socket.id);
    adminIo.emit('removeClient',socket.id);
  });

  // Setup the new share request handler
  socket.on('needNewShare', (msg) => {
    if (!gameOver) {
      console.info(`Client needs new share [id=${socket.id}]`);

      // Get the next share for it to work on
      let shareObj = GameMan.getNewShareObjForWorker(socket);

      // If there are no shares to hand out, tell the worker to idle
      if (shareObj == null) {
        console.info(`No shares left to hand out`);
        socket.emit('idle');
      }
      else {
        console.info(`Sending new share ${shareObj.share}`);
        socket.emit('newShare', shareObj);

        if(msg.newClient){ //occurs when there is a new client
            console.info('ADDING CLIENT TO CLIENT DICT');
            let myNum = shareObj.share[0];
            clientDict.set(socket.id,myNum);
            adminIo.emit('addClient',{id:socket.id,num:myNum});
        }else { //when exisiting client wants new share 
          let myNum = shareObj.share[0];
          clientDict.set(socket.id,myNum);
          console.info('switching the nums');
          let transitString = JSON.stringify(Array.from(clientDict));
          adminIo.emit('numberSwitch',transitString);
        }
      }

      
    }
  });

  // Setup the completed share request handler
  // This is for shares that are not claimed to be winners
  socket.on('completedShare', (msg) => {
    console.info(`Client completed a share [share=${msg.share} id=${socket.id}]`);
    let share = msg.share;
    let wasRejected = GameMan.reportCompletedShare(socket, share);

    if (wasRejected) {
      console.info(`share rejected`);
      socket.emit('shareRejected');
    }
    else {
      console.info(`share accepted`);
      socket.emit('shareAccepted');
    }

  });

  // This handles shares that claim to be winners
  socket.on('iAmAWinner', (msg) => {

    if (gameOver) {
      return;
    }

    let share = msg.share;
    let id = msg.id;
    let isWinningShare = GameMan.isWinningShare(share);

    console.log(`Checking for winning share...`);

    if (isWinningShare) {
      let wasRejected = GameMan.reportCompletedShare(socket, share);

      if (wasRejected) {
        socket.emit('youDidNotWin');
        return;
      }

      console.log(`Got a WINNER!`);

      // Emit to everyone EXCEPT this worker that won
      socket.broadcast.emit('weGotAWinner');

      //emit to admin that we have a winner and which worker it is
      adminIo.emit('weGotAWinner', id);

      // Let the worker know that it did in fact win
      socket.emit('youAreTheWinner');

      // Set the game state to over
      gameOver = true;
    }
    else {
      // Just in case the share is actually a losing share
      socket.emit('youDidNotWin');
    }
  });

  // Handle a request to restart the game
  socket.on('restartGame', (msg) => {
    console.log(`Restarting game with current workers! - CLIENT`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    clientDict = new Map();
    // Tell all the players we restarted
    io.emit('restartGame');
    adminIo.emit('restartGame');
  });

  // Let the client know they are registered
  socket.emit('registered');

  socket.on('buttonPressed', (msg) =>{
    
    if(clientDict.has(msg.id)){
      console.info('switching the nums');
      clientDict.set(msg.id,msg.currNum);
      console.log("ID " + msg.id + " num "+ msg.currNum + " map size " + clientDict.size);

      let transitString = JSON.stringify(Array.from(clientDict));
      adminIo.emit('numberSwitch',transitString);

    }else {
      console.log('something went wrong - server - buttonPressed')
    }
  });



});

// Update the page time every second
setInterval(() => {
  clientIo.emit('time', new Date().toTimeString());
}, 1000);

// Update the page time every second for admin
// setInterval(() => {
//   adminIo.emit('time', new Date().toTimeString());
// }, 1000);

// Refresh display/admin every 30 seconds
setInterval(() => {
  console.info('calling client response');
  adminIo.emit('requestRefresh', new Date().toTimeString());
}, 1000000);





// socket.on('returnClientNumber', (msg) => {
//   //populate dictionary
//   //console.info("heres the number");
//   //console.info(msg[0] + " " + msg[1]);
//   numberDict[msg[0]] = msg[1];
//   if (Object.keys(numberDict).length == (GameMan.getClientSize())) { //dictionary is full 
//     console.info('going to dict');
//     adminIo.emit('getClientDict', numberDict); //send dictionary to admin
//   }
// });


// socket.on('askClientResponse', (msg) => {
//   console.info("ask client response - admin");
//   numberDict = {}; //need to clear dict each time this is called
//   clientIo.emit('getClientNumber');
// });