
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

  #maxNums;
  #shareSize;
  #clients;
  #incompleteShares;
  #winningNum;
  #inProgressShares;
  #repeatSharesIdx;
  #completedShares;

  // Let's set up the game to play
  // We assume maxNums > shareSize and only 
  // account for this case
  constructor(maxNums, shareSize){
    console.log('Starting new game...');

    // Setup the game. This means the client list
    // and the problem space for the clients to explore
    this.#maxNums = maxNums;
    this.#shareSize = shareSize;
    this.#clients = new Map();
    this.#incompleteShares = [];

    // These are to track the shares that are being worked on
    this.#inProgressShares = [];
    this.#repeatSharesIdx = 0;

    // This is to track the completed shares
    this.#completedShares = [];

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
      this.#incompleteShares.push(share);
    }

    // Once all the shares have been prepared, they can be
    // distributed for work.
    // We also select a winning number at random that is
    // shipped with each share for quick verification of 
    // having found a winner
    this.#winningNum = Math.floor(Math.random()*this.#maxNums) + 1;

    console.log('New game started.');
    console.log(`Winning Num: ${this.#winningNum}`);
    console.log('Shares: ',JSON.stringify(this.#incompleteShares));
  }


  // Add a player to the game, needs to be by socket
  // as the socket is the identifier
  addWorker(socket){
    console.info(`Adding player [id=${socket.id}]`);

    // Map the socket to its assigned chunks
    this.#clients.set(socket, {acceptedShares:0, rejectedShares:0});
  }

  // Remove player by socket
  removeWorker(socket){
    console.info(`Removing player [id=${socket.id}]`);

    // Remove the client
    this.#clients.delete(socket);
  }

  // Share comparison function
  #areSharesEqual(shareA, shareB){
      if(shareA.length !== shareB.length){
        return false;
      }
      shareA.forEach(shareAItem => {
        if(!shareB.includes(shareAItem)){
          return false;
        }
      });
      return true;
  }

  // Report to the game manager that the worker completed their share
  // It is assumed that this share is NOT the winning share
  reportCompletedShare(socket, share){
    console.info(`Accepting share ${share} from [id=${socket.id}]`);

    let clientData = this.#clients.get(socket);
    let rejected = false;

    // Check if the share is already in the completion list
    // if it is, then we increment the rejected shares of this worker
    this.#completedShares.forEach(complShare => {
      if(this.#areSharesEqual(complShare, share)){
        clientData.rejectedShares++;
        rejected = true;
        break;
      }
    });

    // Otherwise, we can add to the number of accepted shares for the worker
    // need to also remove the share from the list of in-progress shares
    if(!rejected){
      // Accept the share they completed and 
      // increment their accepted share count
      clientData.acceptedShares++;

      // Add the share to the completion list
      this.#completedShares.append(share);

      // Remove the share from the in-progress list
      this.#inProgressShares.forEach(function(inProgShare, index, object) {
          if (this.#areSharesEqual(inProgShare, share)) {
                object.splice(index, 1);
          }
      });
    }

    return rejected;
  }

  // Request a new chunk of work
  getNewShareObjForWorker(socket){
    console.info(`Assigning new share to [id=${socket.id}]`);

    // If we have enough shares to hand out
    if(this.#incompleteShares.length > 0){

      // Remove the first share from the share list
      var nextShare = this.#incompleteShares.splice(0,1)[0];

      // Consider the share to be in-progress
      this.#inProgressShares.append(nextShare);

      // Return the share and the winning number
      return {share:nextShare, winNum:this.#winningNum};
    }

    // No more shares left to hand out
    // but we have in-progress shares
    else if(this.#inProgressShares.length > 0){

      // Let's hand out the in-progress shares
      // in a round-robin style. This will duplicate
      // work, in the hopes that faster workers explore
      // the leftover space faster
      let nextShare = this.#inProgressShares[this.#repeatSharesIdx];
      this.#repeatSharesIdx = (this.#repeatSharesIdx+1) % this.#inProgressShares.length;

      return {share:nextShare, winNum:this.#winningNum};
    }
    else{
      // If we have 0 work to hand out, tell the worker to wait
      return null;
    }
  }

  isWinningShare(share){
    // let's check if we have a winner
    return share.includes(this.#winningNum);
  }

  // For the server to check if the game is over
  isGameOver(){
    return false;
  }

  // Restart the game with all the players still connected
  restartGameWithCurrentWorkers(){
    return this.#clients;
  }

  // Allow the server to retrieve a list of the clients
  getClients(){
    return this.#clients;
  }

}



