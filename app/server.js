const express = require('express');
//const WebSocket = require('ws');
const socketIO = require('socket.io');
//const { Client } = require('socket.io/dist/client');
const GameManager = require('./gameManager.js');
const ClientObj = require('../public/js/ClientObj.js');
const { param } = require('express/lib/request');
//import ClientObj from '../public/js/ClientObj.js';
//const { parse } = require('ws/lib/extension');
const measurements = require('./measurements.json');

const PORT = process.env.PORT || 3000; 
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

// the global variable indicating the game 
// state for arduinos, only changed by the
// button on the admin panel. Will say "ready"
// when the game is ready for the arduinos
var arduinoGameState = 'waiting';

app.use(
  express.urlencoded({
    extended: true
  })
)

app.use(express.json())

app.set('/ardiono', io);
app.set('/measure', io);

app.get('/arduino', (req,res)=>{
  res.send(arduinoGameState);
})

app.post('/arduino', (req, res)=>{
  console.info(req.body); // the field named IP
  var newSeq = generateTappingSequence();
  res.send(newSeq);
})

/* Kinematic(double SB, double WB, double UB,
		double sP, double wP, double uP, 
		double OX, double OY, double L_min, 
		double L_max, double l, double h); */
app.get('/measure', (req,res)=>{
  console.info(req.headers);
  var mac = req.headers['measure'];
  console.info(measurements[mac]);
  res.send(measurements[mac]);
})

function generateTappingSequence(){
  var arr = "";
  while(arr.length < 3){
      var r = Math.floor(Math.random() * 3) + 1;
      if(arr.indexOf(r) === -1) arr+=r;
  }
  console.log(arr);
  return arr;
}

//---------------------- Arduino ends ---------------------------

// Now let's setup a new GameManager instance
let GameMan = new GameManager(10, 4);

// Keep track of whether we need to restart the game
let gameOver = false;

var arduinoObj = {key: "hello world"};

let winningClient = ""; //id of winningClient //dont think we use this???

const clientNames = ["Abraham Lincoln", "George Washington", "Ben Franklin", "Ada Lovelace", 
"Martin Luther King Jr.",  "Malcolm X", "Louis Armstrong", "Frank Sinatra", "Henry Ford", 
"Sacagawea", "Steve Jobs", "Muhammad Ali", "Harriet Tubman", "Grace Hopper"];

const chosenClients = [];

const chosenColors = [];

const clientColors =  ['#FE9',"#AFA","#FA7", '#9AF','#FFEFD5','#C2F0D1',"#FFB6C1","#D9D7FA"];//'#9AF','#F9A', '#E2CFE2'

let clientDict = new Map(); //map of client ids to client objects



//Namespaces for client/admin/arduino
const adminIo = io.of('/admin.html');

const clientIo = io.of('/');

const arduinoIo = io.of('/arduino.html');

//generates a random color
function generateColor(){
  if (chosenColors.length === 0){
    for (var i = 0; i < clientColors.length; i++) chosenColors.push(i);
  }
  var randomValueIndex = Math.floor(Math.random() * chosenColors.length);
  var indextOfItemInMyArray = chosenColors[randomValueIndex];
  chosenColors.splice(randomValueIndex,1);
  return clientColors[indextOfItemInMyArray];
}

//generates a random name
function generateName() {
  if (chosenClients.length === 0){
    for (var i = 0; i < clientNames.length; i++) chosenClients.push(i);
  }
  var randomValueIndex = Math.floor(Math.random() * chosenClients.length);
  var indextOfItemInMyArray = chosenClients[randomValueIndex];
  chosenClients.splice(randomValueIndex,1);
  return clientNames[indextOfItemInMyArray];
}

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
    console.log(`Restarting game with current workers! - ADMIN`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    winningClient = "";
    // Tell all the players we restarted
    adminIo.emit('restartGame');
    io.emit('restartGame');
  });

  //updating arduino status
  socket.on('updateArdStatus', (msg) => {
    arduinoGameState = msg;
    console.log("The arduino status has changed to " + arduinoGameState);
  })
  //updates game parameters
  socket.on('setNewGameParams', (msg) =>{
    console.log('Changing the game parameters');
    GameMan.resetGameParameters(msg);
    console.info(`Restarting game with current workers! - ADMIN`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    winningClient = "";
    // Tell all the players we restarted
    io.emit('restartGame');
    adminIo.emit('restartGame');

    GameMan.updateWinningNum(msg[2]);
    io.emit('updateWinningNumber',msg[2]);
    //adminIo.emit('updateWinningNumber');
  });

  socket.on('getParams', (msg) => {
    let params = GameMan.getParams();
    socket.emit('updateParams',params);
  })

  //initial registration
  let transitString = JSON.stringify(Array.from(clientDict));
  let params = GameMan.getParams();
  socket.emit('registered',{map: transitString, par: params, ardStatus: arduinoGameState}); 
  //when admin is added, pass client dictionary, current parameters, arduino status and populate screen

});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// Handle a new client connection
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
        let myNum = shareObj.share[0];

        if(!(clientDict.has(socket.id))){ //occurs when there is a new client
            console.info('ADDING NEW CLIENT OBJ TO CLIENT DICT');
            let newName = generateName();
            let newColor = generateColor();
            var newC = new ClientObj(newName,socket.id,newColor,myNum);
            clientDict.set(socket.id,newC);
            adminIo.emit('addClient',{id:socket.id, obj: newC});
            socket.emit('getMyInfo', {color: newColor, name: newName});
        }else { //when exisiting client wants new share 

          let currClient = clientDict.get(socket.id);
          currClient.num = myNum;
          console.info('switching the nums2');
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
      console.log("WERE GETTING THE WINNING SHARE")
      let wasRejected = GameMan.reportCompletedShare(socket, share);

      if (wasRejected) {
        console.log('BOO I GOT REJECTED');
        socket.emit('youDidNotWin');
        return;
      }

      winningClient = socket.id; //save id of winning client

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
    //clientDict = new Map();
    winningClient = "";
    // Tell all the players we restarted
    io.emit('restartGame');
    adminIo.emit('restartGame');
  });


  // Let the client know they are registered
  socket.emit('registered', {gameStatus: gameOver});

  //let admin panel know a client has switched numbers
  socket.on('buttonPressed', (msg) =>{
    
    if(clientDict.has(msg.id)){
      console.info('switching the nums1');
      let thisC = clientDict.get(msg.id);
      thisC.num = msg.currNum;
      console.log("ID " + msg.id + " num "+ msg.currNum + " map size " + clientDict.size);

      let transitString = JSON.stringify(Array.from(clientDict));
      adminIo.emit('numberSwitch',transitString);

    }else {
      console.log('something went wrong - server - buttonPressed')
    }
  });



});

arduinoIo.on('connection', (socket) => {
  socket.emit("registered", arduinoObj);
});

// Update the page time every second
setInterval(() => {
  clientIo.emit('time', new Date().toTimeString());
}, 1000);

// Update the page time every second for admin
setInterval(() => {
  adminIo.emit('time', new Date().toTimeString());
}, 1000);

// Refresh display/admin every 30 seconds
setInterval(() => {
  console.info('calling client response');
  adminIo.emit('requestRefresh', new Date().toTimeString());
}, 1000000);


//old code below


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