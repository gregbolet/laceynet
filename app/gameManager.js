
/**
 * The purpose of this class is to run an entire exploration
 * of the problem space [1, maxNums]. We assign chunks of this
 * problem space to each of the players. When a player is done
 * with their work, we accept their share of work. The player
 * should then request a new chunk of work and explore it.
 * We perform this exploration until one of the workers has 
 * found the winning number. 
 * After the winning number is found, we can restart the game.
 * */
module.exports = class GameManager{

  static #maxNums;
  static #shareSize;
  static #clients;
  static #incompleteShares;
  static #winningNum;
  static #inProgressShares;
  static #repeatSharesIdx;
  static #completedShares;
  static #isGameOver;
  static #ledger;

  #generateShares(){

    let maxNums = GameManager.#maxNums;
    let shareSize = GameManager.#shareSize;

    // These are to track the shares that are being worked on
    GameManager.#incompleteShares = [];
    GameManager.#inProgressShares = [];
    GameManager.#completedShares = [];

    // This tells us where we are in the RR inProgress Shares
    // that will be handed out when we run out of incompleteShares
    GameManager.#repeatSharesIdx = 0;

    let allNums = [];

    // Create an array from 1 to maxNums
    // This will be our global problem
    for(;maxNums > 0; maxNums--){
      allNums.push(maxNums);
    }

    // Now let's create shares of this entire space
    // (i.e: partition the search space into workable chunks)
    // Usually this partitioning would be done s.t. each chunk
    // is composed of consecutive numbers, but for sake of example
    // we will RANDOMLY partition the exploration space.
    //
    //While we haven't run out of numbers
    while(allNums.length !== 0){

      // Grab numbers at random equal to the share size
      // There may be a share at the end which has less than
      // the expected share size.
      let share = [];
      let toGrab = shareSize;

      // If we can't grab as many as we need
      if(shareSize > allNums.length){
        toGrab = allNums.length;
      }

      for(;toGrab > 0; toGrab--){
        // remove an item at random from the list
        let randIdx = Math.floor(Math.random()*allNums.length);
        var val = allNums.splice(randIdx,1)[0];
        share.push(val); 
      }

      // Once we construct the share, add it to the list
      GameManager.#incompleteShares.push(share);
    }

    // Once all the shares have been prepared, they can be
    // distributed for work.
    // We also select a winning number at random that is
    // shipped with each share for quick verification of 
    // having found a winner
    
    GameManager.#winningNum = Math.floor(Math.random()*GameManager.#maxNums) + 1;
    

    

    console.log(`Winning Num: ${GameManager.#winningNum}`);
    console.log('Shares: ',JSON.stringify(GameManager.#incompleteShares));
  }

  // Let's set up the game to play
  // We assume maxNums > shareSize and only 
  // account for this case
  constructor(maxNums, shareSize){
    console.log('Starting new game...');

    // Setup the game. This means the client list
    // and the problem space for the clients to explore
    GameManager.#maxNums = maxNums;
    GameManager.#shareSize = shareSize;
    GameManager.#clients = new Map();
    GameManager.#isGameOver = true;
    GameManager.#ledger = [];

    this.#generateShares();

    console.log('New game started.');
  }


  // Add a player to the game, needs to be by socket
  // as the socket is the identifier
  addWorker(socket){
    console.info(`Adding player [id=${socket.id}]`);

    // Map the socket to its assigned chunks
    GameManager.#clients.set(socket, {acceptedShares:0, rejectedShares:0});
  }

  // Remove player by socket
  removeWorker(socket){
    console.info(`Removing player [id=${socket.id}]`);

    // Remove the client
    GameManager.#clients.delete(socket);
  }

  // Share comparison function
  static #areSharesEqual(shareA, shareB){
    if(shareA.length !== shareB.length){
      return false;
    }

    let equal = true;
    shareA.every(shareAItem => {
      if(!shareB.includes(shareAItem)){
        equal = false;
        return false;
      }
      return true;
    });

    return equal;

  }

  // Report to the game manager that the worker completed their share
  // It is assumed that this share is NOT the winning share
  reportCompletedShare(socket, share){
    console.info(`Accepting share ${share} from [id=${socket.id}]`);

    let clientData = GameManager.#clients.get(socket);
    let rejected = false;

    // Check if the share is already in the completion list
    // if it is, then we increment the rejected shares of this worker
    GameManager.#completedShares.every(complShare => {
      if(GameManager.#areSharesEqual(complShare, share)){
        clientData.rejectedShares++;
        rejected = true;
        return false;
      }
      return true;
    });

    // Otherwise, we can add to the number of accepted shares for the worker
    // need to also remove the share from the list of in-progress shares
    if(!rejected){
      // Accept the share they completed and 
      // increment their accepted share count
      clientData.acceptedShares++;

      // Add the share to the completion list
      GameManager.#completedShares.push(share);

      // Remove the share from the in-progress list
      GameManager.#inProgressShares.forEach(function(inProgShare, index, object) {
        if (GameManager.#areSharesEqual(inProgShare, share)) {
          object.splice(index, 1);
        }
      });
    }

    return rejected;
  }

  // Request a new chunk of work
  getNewShareObjForWorker(socket){
    //console.info(`Assigning new share to [id=${socket.id}]`);

    console.log('Incomplete Shares: ',JSON.stringify(GameManager.#incompleteShares));
    console.log('In-Progress Shares: ',JSON.stringify(GameManager.#inProgressShares));
    console.log('Completed Shares: ',JSON.stringify(GameManager.#completedShares));

    // If we have enough shares to hand out
    if(GameManager.#incompleteShares.length > 0){

      // Remove the first share from the share list
      var nextShare = GameManager.#incompleteShares.splice(0,1)[0];

      // Consider the share to be in-progress
      GameManager.#inProgressShares.push(nextShare);
      console.info(`Share from incomplete list [${nextShare}]`);

      // Return the share and the winning number
      return {share:nextShare, winNum:GameManager.#winningNum};
    }

    // No more shares left to hand out
    // but we have in-progress shares
    else if(GameManager.#inProgressShares.length > 0){

      console.log('Repeat shares idx: ', GameManager.#repeatSharesIdx)

      // Let's hand out the in-progress shares
      // in a round-robin style. This will duplicate
      // work, in the hopes that faster workers explore
      // the leftover space faster
      if(GameManager.#repeatSharesIdx >= GameManager.#inProgressShares.length){
        GameManager.#repeatSharesIdx = 0;
      }

      let nextShare = GameManager.#inProgressShares[GameManager.#repeatSharesIdx++];


      console.info(`Share from in-progress list [${nextShare}]`);

      return {share:nextShare, winNum:GameManager.#winningNum};
    }
    else{
      // If we have 0 work to hand out, tell the worker to wait
      console.info(`Idle signal to be sent`);
      return null;
    }
  }

  isWinningShare(share){
    // let's check if we have a winner
    // console.log('type of winning number: ' + typeof(GameManager.#winningNum));
    // console.log("my share "+ share);
    // console.log("winning number: " + GameManager.#winningNum);
    // console.log("the winning share is in here?: " + share.includes(GameManager.#winningNum));
    return share.includes(GameManager.#winningNum);
  }

  // Restart the game with all the players still connected
  restartGameWithCurrentWorkers(){

    // Regenerate all the shares
    this.#generateShares();

    GameManager.#clients.forEach((clientData, client) => {
      clientData.acceptedShares = 0;
      clientData.rejectedShares = 0;
    });

    console.log('New game started.');
    console.log('Current parameters: ' + GameManager.#maxNums + " range and " + GameManager.#shareSize +" share size");
  }

  // Allow the server to retrieve a list of the clients
  getClients(){
    return GameManager.#clients;
  }

  resetGameParameters(input){
    console.log('Resetting parameters...');
    let newRange = parseInt(input[0]);
    let newShareSize = parseInt(input[1]);
    // Setup the game. This means the client list
    // and the problem space for the clients to explore
    GameManager.#maxNums = newRange;
    GameManager.#shareSize = newShareSize;
  }

  updateWinningNum(newWin){
    //console.log("THE NEW WINNING NUMBER IS " + newWin);
    GameManager.#winningNum = parseInt(newWin);
    console.log("The new winning number is " + GameManager.#winningNum);
  }

  getWinningNum(){
    return GameManager.#winningNum;
  }

  getLedger(){
    return GameManager.#ledger
  }

  setLedger(num){
    GameManager.#ledger.push(num);
  }

  updateLedger(num){
    if(GameManager.#ledger.length >= 7){
      GameManager.#ledger.shift();
    }
    GameManager.#ledger.push(num);
    return GameManager.#ledger;
  }

  getParams() {
    let params = [GameManager.#maxNums,GameManager.#shareSize, GameManager.#winningNum];
    return params;
  }

  getClientIDs(){  //don thibk i need this anymore
    var clientinfo ="";
    var count = 1;
    GameManager.#clients.forEach((clientData, client) => {
      if(count >= GameManager.#clients.size){
        clientinfo += JSON.stringify("Display: "  + client.id, null, 2)
      }else {
        clientinfo += JSON.stringify("Client " + count + ": " + client.id, null, 2)
      }
      count++;
    })
    
    return clientinfo;
  }

  getMyClients(){  //returns array of client id's //can probably delete this
    var arrayOfIDs = [];
    var count = 0;
    GameManager.#clients.forEach((clientData, client) => {
      arrayOfIDs[count] = client.id;
      count++;
    })
    return arrayOfIDs;
  }

  getClientSize() {
    return GameManager.#clients.size;
  }

  getIsGameOver(){
    return GameManager.#isGameOver;
  }

  startGame() {
    GameManager.#isGameOver = false;
  }

  endGame() {
    GameManager.#isGameOver = true;
  }



}



