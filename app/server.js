const express = require('express');
const socketIO = require('socket.io');
const GameManager = require('./gameManager.js');
const ClientObj = require('../public/js/ClientObj.js');
const { param } = require('express/lib/request');
const measurements = require('./measurements.json');

const PORT = process.env.PORT || 5000; 
const app = express();
const server = app.listen(PORT, function () {
  console.log(`Game Server UI listening on port ${PORT}!`)
});
// socketIO will serve the websockets and handle reverse
// compatibility and protocol fallback
const io = socketIO(server);


// Serve all the files from the /public folder
// Given public/index.html it will be served from myaddress.com/index.html
app.use(express.static('public'))  
app.use(express.urlencoded({extended: true}))
app.use(express.json())


// the global variable indicating the game 
// state for arduinos, only changed by the
// button on the display panel. Will say "ready"
// when the game is ready for the arduinos
var arduinoGameState = 'waiting';



app.set('/ardiono', io);
app.get('/arduino', (req,res)=>{
  console.info(req.headers);
  var data = {};
  if (req.headers.hasOwnProperty('measure')){
    var mac = req.headers['measure'];
    console.info(measurements[mac]);
    data['measurement'] = measurements[mac];
  }
  data['gameState'] = arduinoGameState;
  res.send(data);
})

//---------------------- Arduino ends ---------------------------

// Now let's setup a new GameManager instance
var GameMan = new GameManager(10, 4);

// Keep track of whether we need to restart the game
var gameOver = false;

var arduinoObj = {key: "hello world"};

var winningClient = ""; //id of winningClient //dont think we use this???

const clientNames = ["Abraham Lincoln", "George Washington", "Ben Franklin", "Ada Lovelace", 
"Martin Luther King Jr.",  "Malcolm X", "Louis Armstrong", "Frank Sinatra", "Henry Ford", 
"Sacagawea", "Steve Jobs", "Muhammad Ali", "Harriet Tubman", "Grace Hopper"];

const chosenClients = [];

const chosenColors = [];

const clientColors =  ['#FE9',"#AFA","#FA7", '#9AF','#FFEFD5','#C2F0D1',"#FFB6C1","#D9D7FA"];//'#9AF','#F9A', '#E2CFE2'

let clientDict = new Map(); //map of client ids to client objects


// define namespaces 
const displayIo = io.of('/display.html');
const adminIo = io.of('/admin.html');
const clientIo = io.of('/');  // client page


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

// socket.emit('registered',{map: transitString, par: params, ardStatus: arduinoGameState}); // i need arduino to admin


// ------------------------- admin namespace -----------------------------
adminIo.on('connection', (socket) => {


  //updating arduino status
  socket.on('updateArdStatus', (msg) => {
    arduinoGameState = msg;
    console.log("The arduino status has changed to " + arduinoGameState);
  });

  //updates game parameters
  socket.on('setNewGameParams', (msg) =>{
    console.log('Changing the game parameters');
    GameMan.resetGameParameters(msg);
    console.info(`Restarting game with current workers! - display`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    winningClient = "";
    // Tell all the players we restarted
    io.emit('restartGame');
    displayIo.emit('displayRestartGame', {gameStatus: gameOver, parameters: params});

    GameMan.updateWinningNum(msg[2]);
    io.emit('updateWinningNumber', msg[2]);
    displayIo.emit('displayUpdateParams');
  });

  socket.on('getParams', () => {
    const stats = GameMan.getParams();
    socket.emit('displayUpdateParams', stats);
  });

  // socket.on('refreshPress', (msg) => { //kind of useless now?
  //   let transitString = JSON.stringify(Array.from(clientDict));
  //   displayIo.emit('displaynumberSwitch',{id: socket.id, newClient: currClient});
  // });

  socket.on('disconnect', () => {
    console.log('admin Client disconnected');
  });

});



// ------------------------- display namespace -----------------------------
displayIo.on('connection', (socket) => {
  console.info(`display Client connected [id=${socket.id}]`);

  //initial registration
  let clientMapping = Object.fromEntries(clientDict);
  let params = GameMan.getParams();
  socket.emit('displayRegistered', {map: clientMapping, parameters: params, gameStatus: gameOver, winner: winningClient});
 
  // Handle a request to restart the game
  socket.on('restartGame', () => {
    console.log(`Restarting game with current workers! - display`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    winningClient = "";
    let newParams = GameMan.getParams();
    // Tell all the players we restarted
    displayIo.emit('displayRestartGame', {gameStatus: gameOver, parameters: newParams});
    io.emit('restartGame');
  });

  socket.on('disconnect', () => {
    console.log('display Client disconnected');
  });

});


// ------------------------- client namespace -----------------------------
function handleNewClient(socket, myNum){
  console.info('ADDING NEW CLIENT OBJ TO CLIENT DICT');
  let newName = generateName();
  let newColor = generateColor();

  const newClient = new ClientObj(newName, socket.id, newColor, myNum);
  clientDict.set(socket.id, newClient); //add to overall dict

  let newMapping = Object.fromEntries(clientDict);
  displayIo.emit('displayNewClient', {map: newMapping, id: socket.id}); // send the updated new Mapping
  socket.emit('registered', {gameStatus: gameOver, color: newColor, name: newName});
  // socket.emit('getMyInfo', {color: newColor, name: newName}); // emit to the client that sent request
}


clientIo.on('connection', (socket) => {
  console.info(`Client connected [id=${socket.id}]`);

  GameMan.addWorker(socket);

  // Let the client know they are registered
  if (!gameOver){
    let shareObj = GameMan.getNewShareObjForWorker(socket); // get share

    // If there are no shares to hand out, tell the worker to idle
    if (shareObj == null) {
      console.info(`No shares left to hand out`);
      socket.emit('idle');
    }
    else{ // new share available
      console.info(`Sending new share ${shareObj.share}`);
      socket.emit('newShare', shareObj);

      let myNum = shareObj.share[0];
      handleNewClient(socket, myNum);
    }
  }
  
  // Setup the new share request handler
  socket.on('needNewShare', () => {
    if (!gameOver) { // game is still ON
      console.info(`Client needs new share [id=${socket.id}]`);

      // Get the next share for it to work on
      let shareObj = GameMan.getNewShareObjForWorker(socket);

      // If there are no shares to hand out, tell the worker to idle
      if (shareObj == null) {
        console.info(`No shares left to hand out`);
        socket.emit('idle');
        return;
      }
      // new share available
      console.info(`Sending new share ${shareObj.share}`);
      socket.emit('newShare', shareObj);
      let myNum = shareObj.share[0];

      //when exisiting client wants new share 
      let currClient = clientDict.get(socket.id);
      currClient.num = myNum;
      displayIo.emit('displayNumberSwitch', {id: socket.id, newClient: currClient});
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

      //emit to display that we have a winner and which worker it is
      displayIo.emit('displayGotAWinner', id);

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
  socket.on('restartGame', () => {
    console.log(`Restarting game with current workers! - CLIENT`);
    GameMan.restartGameWithCurrentWorkers();
    gameOver = false;
    winningClient = "";

    // Tell all the players we restarted
    io.emit('restartGame');
    displayIo.emit('displayRestartGame', {gameStatus: gameOver});
  });

  //let display panel know a client has switched numbers
  socket.on('buttonPressed', (msg) =>{
    
    if(clientDict.has(msg.id)){
      console.info('switching the nums1');
      let thisC = clientDict.get(msg.id);
      thisC.num = msg.currNum;
      console.log("ID " + msg.id + " num "+ msg.currNum + " map size " + clientDict.size);

      // let transitString = JSON.stringify(Array.from(clientDict));
      displayIo.emit('displayNumberSwitch', {id: msg.id, newClient: thisC});

    }else {
      console.log('something went wrong - server - buttonPressed')
    }
  });

  // Set the socket disconnect event handler
  socket.on('disconnect', () => {
    console.log('Client disconnected');
    GameMan.removeWorker(socket);
    clientDict.delete(socket.id);
    let newMapping = Object.fromEntries(clientDict);
    displayIo.emit('displayremoveClient', {map: newMapping, id: socket.id});
  });

});










// ------------------------- extra functionality -----------------------------

// Update the page time every second
setInterval(() => {
  clientIo.emit('time', new Date().toTimeString());
}, 1000);

// Update the page time every second for display
setInterval(() => {
  displayIo.emit('time', new Date().toTimeString());
}, 1000);

// Refresh display/display every 30 seconds
setInterval(() => {
  console.info('calling client response');
  displayIo.emit('requestRefresh', new Date().toTimeString());
}, 1000000);