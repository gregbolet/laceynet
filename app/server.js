const express = require('express');
const socketIO = require('socket.io');
const GameManager = require('./gameManager.js');
const ClientObj = require('../public/js/ClientObj.js');
const { param } = require('express/lib/request');
const People = require('../public/js/images.js');

const measurements = require('./measurements.json');
const IP_UPPER = 41;
const IP_LOWER = 12;
const NUM_TABLET = 30;
const NUM_FALSE = 0.1 * NUM_TABLET; // 3 false 


const PORT = process.env.PORT || 5000; 
const app = express();
const server = app.listen(PORT, function () {
  console.log(`Game Server UI listening on port ${PORT}!`)
});
// socketIO will serve the websockets and handle reverse
// compatibility and protocol fallback
const io = socketIO(server);
const speed_list = generateSpeed(10, 301, 10);

var hist = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
var emits = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];

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

function generateSpeed(start, end, len){
  const slist = [];
  for (var i = 0; i < len; i++) {
    let one = Math.floor(Math.random() * (start, end)) + start;
    slist.push(one);
  }
  console.log("the new speed list: " + slist);
  return slist;
}

app.set('/arduino', io);
app.get('/arduino', (req,res)=>{
  hist[15] += 1;
  //console.info(req.headers);
  var data = {};
  if (req.headers.hasOwnProperty('measure')){
    var mac = req.headers['measure'];
    data['measurement'] = measurements["measurement"]; // everyone gets the same
    data['offsets'] = measurements[mac];
    data['speed'] = speed_list[measurements[mac]["index"]];
  }
  data['gameState'] = arduinoGameState;
  console.log(data);
  res.send(data);
})

//---------------------- Arduino ends ---------------------------

// Now let's setup a new GameManager instance
var GameMan = new GameManager(10, 4);

var winningClient = ""; //id of winningClient //dont think we use this???

const clientNames = People.names;

const chosenClients = [];

const chosenColors = [];

const clientColors =  ['#FE9',"#AFA","#FA7", '#9AF','#FFEFD5','#C2F0D1',"#FFB6C1","#D9D7FA"];//'#9AF','#F9A', '#E2CFE2'

let clientDict = new Map(); //map of client ids to client objects
var rebel_pos = [];

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

//gets image based on given name
function getImage(name){
  if(Object.keys(People.JPGIcons).includes(name)){
    return People.JPGIcons[name];
  }
}

// ------------------------- admin namespace -----------------------------
adminIo.on('connection', (socket) => {

  hist[0] += 1;

  emits[0] += 1;
  rebel_pos = pickRebel();
  socket.emit('registered', {isGameOver:GameMan.getIsGameOver(), arduinoStatus: arduinoGameState});

  socket.on('startGame', (msg) => {

    hist[1] += 1;
    GameMan.startGame();
    console.log('THE GAME IS STARTED - ', GameMan.getIsGameOver());
    console.log(`Restarting game with current workers! - ADMIN`);
    GameMan.restartGameWithCurrentWorkers();
    winningClient = "";
    // Tell all the players we restarted
    emits[1] += 1;
    adminIo.emit('restartGame');
    emits[2] += 1;
    io.emit('restartGame');
    let params = GameMan.getParams();
    console.log('HERE ARE THE PARAMETERS - ', params);
    let clientMapping = Object.fromEntries(clientDict);
    let winLedger = GameMan.getLedger();
    emits[3] += 1;
    displayIo.emit('displayStartGame', {map: clientMapping, parameters: params, isGameOver: GameMan.getIsGameOver(), winner: winningClient, ledger: winLedger});
  });

  //updating arduino status
  socket.on('updateArdStatus', (msg) => {
    hist[2] += 1;
    arduinoGameState = msg;
    emits[4] += 1;
    socket.broadcast.emit('checkArdStatus', arduinoGameState);
    console.log("The arduino status has changed to " + arduinoGameState);
  });

  //updates game parameters
  socket.on('setNewGameParams', (msg) =>{
    hist[3] += 1;
    console.log('Changing the game parameters');
    console.log(msg)
    GameMan.resetGameParameters(msg);
    console.info(`Restarting game with current workers! - display`);
    GameMan.restartGameWithCurrentWorkers();
    GameMan.startGame();
    winningClient = "";
    let winLedger = GameMan.getLedger();
    // Tell all the players we restarted
    
    emits[5] += 1;
    io.emit('restartGame');
    emits[6] += 1;
   displayIo.emit('displayRestartGame', {isGameOver: GameMan.getIsGameOver(), parameters: msg, ledger:winLedger});
    emits[7] += 1;
    adminIo.emit('restartGame');
    GameMan.updateWinningNum(msg[2]);
    emits[8] += 1;
    io.emit('updateWinningNumber', msg[2]);
    emits[9] += 1;
    displayIo.emit('displayUpdateParams', msg);
  });

  socket.on('getParams', () => {
    hist[4] += 1;
    const stats = GameMan.getParams();
    emits[10] += 1;
    socket.emit('displayUpdateParams', stats);//change to display io
  });

  socket.on('restartGame', (msg) => {
    hist[5] += 1;
    console.log(`Restarting game with current workers! - ADMIN`);
    GameMan.restartGameWithCurrentWorkers();
    winningClient = "";
    GameMan.startGame();
    // Tell all the players we restarted
    emits[11] += 1;
    adminIo.emit('restartGame');
    emits[12] += 1;
    io.emit('restartGame');
  })

  socket.on('disconnect', () => {
    hist[6] += 1;
    console.log('admin Client disconnected');
  });

});



// ------------------------- display namespace -----------------------------
displayIo.on('connection', (socket) => {
  hist[7] += 1;
  console.info(`display Client connected [id=${socket.id}]`);

  //initial registration
  let clientMapping = Object.fromEntries(clientDict);
  let params = GameMan.getParams();
  let winLedger = GameMan.getLedger();
  console.log(winningClient);
  emits[13] += 1;
  socket.emit('displayRegistered', {map: clientMapping, parameters: params, isGameOver: GameMan.getIsGameOver(), winner: winningClient, ledger: winLedger});
 


  socket.on('disconnect', () => {
    hist[8] += 1;
    console.log('display Client disconnected');
  });

});


// ------------------------- client namespace -----------------------------
function handleNewClient(socket, myNum, survey, consensusStatus){
  console.info('ADDING NEW CLIENT OBJ TO CLIENT DICT ');
  let newName = generateName();
  let newColor = generateColor();
  let newImg = getImage(newName);
  const newClient = new ClientObj(newName, socket.id, newColor, myNum,newImg);
  clientDict.set(socket.id, newClient); //add to overall dict
  let newMapping = Object.fromEntries(clientDict);
  emits[14] += 1;
  displayIo.emit('displayNewClient', {map: newMapping, id: socket.id}); // send the updated new Mapping
  emits[15] += 1;
  socket.emit('registered', {isGameOver: GameMan.getIsGameOver(), 
    color: newColor, name: newName, img: newImg, dispSurvey: survey, conStatus: consensusStatus});
}

function pickRebel(){
  var res = [];
  var counter = 0;
  while(counter < NUM_FALSE){
    let temp = Math.floor(Math.random() * NUM_TABLET);
    if (!res.includes(temp)){
        res.push(temp);
        counter ++;
    }
  }
  return res;
}

clientIo.on('connection', (socket) => {
  let addr = socket.handshake.address;
  var idx = addr.lastIndexOf(':');
  if (~idx && ~addr.indexOf('.')){
    addr = addr.slice(idx + 1);
  }
  console.log('New connection from IP address: ' + addr);
  const ipList = addr.split('.');
  let dispSurvey = true;
  let consensusStatus = -1; // default
  if ((ipList[0] == "192") && (ipList[1] == "168") && (ipList[2] == "0") 
    && (IP_LOWER <= parseInt(ipList[3])) && (parseInt(ipList[3]) <= IP_UPPER)){
      console.log((ipList[0] == '192'),(ipList[1] == '168'), (ipList[2] == '0') , (IP_LOWER <= parseInt(ipList[3]) <= IP_UPPER));
      dispSurvey = false;
      if (rebel_pos.includes(connection_counter)){
        console.log("Sending a rebel!!");
        consensusStatus = 0; // false, become a rebel
      }
      else{
        consensusStatus = 1; // true
      }
  }

  hist[9] += 1;
  console.info(`Client connected [id=${socket.id}]`); //MOVE CLIENT CONNECTION TOT HE BOTTOM

  GameMan.addWorker(socket);

  // Let the client know they are registered
  if (!GameMan.getIsGameOver()){ //playing
    let shareObj = GameMan.getNewShareObjForWorker(socket); // get share

    // If there are no shares to hand out, tell the worker to idle
    if (shareObj == null) {
      console.info(`No shares left to hand out`);
      emits[16] += 1;
      socket.emit('idle');
    }
    else{ // new share available
      console.info(`Sending new share ${shareObj.share}`);
      emits[17] += 1;
      socket.emit('newShare', shareObj);

      let myNum = shareObj.share[0];
      handleNewClient(socket, myNum, dispSurvey, consensusStatus);
    }
  }
  else { //doesnt get a share client //not playing
    handleNewClient(socket, -1, dispSurvey, consensusStatus);
  }
  
  // Setup the new share request handler
  socket.on('needNewShare', () => {
    hist[10] += 1;
    if (!GameMan.getIsGameOver()) { // game is still ON
      console.info(`Client needs new share [id=${socket.id}]`);

      // Get the next share for it to work on
      let shareObj = GameMan.getNewShareObjForWorker(socket);

      // If there are no shares to hand out, tell the worker to idle
      if (shareObj == null) {
        console.info(`No shares left to hand out`);
        emits[18] += 1;
        socket.emit('idle');
        return;
      }
      // new share available
      console.info(`Sending new share ${shareObj.share}`);
      emits[19] += 1;
      socket.emit('newShare', shareObj);
      let myNum = shareObj.share[0];

      //when exisiting client wants new share 
      let currClient = clientDict.get(socket.id);
      currClient.num = myNum;
      console.log('GOT MY NEW NUMBER WOOHOO - ',currClient.num);
      emits[20] += 1;
      displayIo.emit('displayNumberSwitch', {id: socket.id, newClient: currClient});
    }
  });

  // Setup the completed share request handler
  // This is for shares that are not claimed to be winners
  socket.on('completedShare', (msg) => {
    hist[11] += 1;
    console.info(`Client completed a share [share=${msg.share} id=${socket.id}]`);
    let share = msg.share;
    let wasRejected = GameMan.reportCompletedShare(socket, share);

    if (wasRejected) {
      console.info(`share rejected`);
      emits[21] += 1;
      socket.emit('shareRejected');
    }
    else {
      console.info(`share accepted`);
      emits[22] += 1;
      socket.emit('shareAccepted');
    }

  });

  // This handles shares that claim to be winners
  socket.on('iAmAWinner', (msg) => {
    hist[12] += 1;
    if (GameMan.getIsGameOver()) {
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
        emits[23] += 1;
        socket.emit('youDidNotWin');
        return;
      }

      winningClient = socket.id; //save id of winning client

      console.log(`Got a WINNER!`);

      // Emit to everyone EXCEPT this worker that won
      emits[24] += 1;
      socket.broadcast.emit('weGotAWinner');

      //emit to display that we have a winner and which worker it is
      let currWinningNum = GameMan.getWinningNum();
      let winnerName = clientDict.get(socket.id).name;
      let space = " ";
      if(GameMan.getLedger().length == 0){
        space = "";
      }
      if (winnerName != ""){

        let winString = space + winnerName + " : " + currWinningNum;

        GameMan.updateLedger(winString);
      }

      emits[25] += 1;
      displayIo.emit('displayGotAWinner', {id: id, winNum: currWinningNum});

      // Let the worker know that it did in fact win
      emits[26] += 1;
      socket.emit('youAreTheWinner');

      // Set the game state to over
      GameMan.endGame();

      arduinoGameState = "waiting";//changing the arduino status bc game over

      emits[27] += 1;
      adminIo.emit('gameEnded');
      emits[28] += 1;
      clientIo.emit('sendSurvey');
      clientIo.emit('sendConsencus');
    }
    else {
      // Just in case the share is actually a losing share
      emits[29] += 1;
      socket.emit('youDidNotWin');
    }
  });



  //let display panel know a client has switched numbers
  socket.on('buttonPressed', (msg) =>{
    hist[13] += 1;
    if(clientDict.has(msg.id)){
      let thisC = clientDict.get(msg.id);
      thisC.num = msg.currNum;
      // console.log("ID " + msg.id + " num "+ msg.currNum + " map size " + clientDict.size);
      emits[30] += 1;
      displayIo.emit('displayNumberSwitch', {id: msg.id, newClient: thisC});
    }
    // else {
    //   console.log('something went wrong - server - buttonPressed ' + thisC.name);
    // }
  });



  // Set the socket disconnect event handler
  socket.on('disconnect', () => {
    hist[14] += 1;
    console.log('Client disconnected');
    GameMan.removeWorker(socket);
    clientDict.delete(socket.id);

    let newMapping = Object.fromEntries(clientDict);
    emits[31] += 1;
    displayIo.emit('displayremoveClient', {map: newMapping, id: socket.id});
  });

});










// ------------------------- extra functionality -----------------------------
setInterval(() => {
  //console.log(hist.toString()); 
  hist.forEach(element => process.stdout.write(element+', '));
  process.stdout.write("\n");

  emits.forEach(element => process.stdout.write(element+', '));
  process.stdout.write("\n");

}, 5000);

// Update the page time every second
setInterval(() => {
  //hist[15] += 1;
  emits[32] += 1;
  clientIo.emit('time', new Date().toTimeString());
}, 1000);

// Update the page time every second for display
setInterval(() => {
  //hist[16] += 1;
  emits[33] += 1;
  displayIo.emit('time', new Date().toTimeString());
}, 1000);

// Refresh display/display every 30 seconds
setInterval(() => {
  //hist[17] += 1;
  console.info('calling client response');
  displayIo.emit('requestRefresh', new Date().toTimeString());
}, 1000000);