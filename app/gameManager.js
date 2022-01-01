
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
  #sharesToExplore;
  #winningNum;

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
    this.#sharesToExplore = [];

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
      this.#sharesToExplore.push(share);
    }

    // Once all the shares have been prepared, they can be
    // distributed for work.
    // We also select a winning number at random that is
    // shipped with each share for quick verification of 
    // having found a winner
    this.#winningNum = Math.floor(Math.random()*this.#maxNums) + 1;

    console.log('New game started.');
    console.log(`Winning Num: ${this.#winningNum}`);
    console.log('Shares: ',JSON.stringify(this.#sharesToExplore));
  }


  // Add a player to the game, needs to be by socket
  // as the socket is the identifier
  addPlayer(socket){
    console.info(`Adding player [id=${socket.id}]`);

    // Map the socket to its assigned chunks
    this.#clients.set(socket, {acceptedShares:[]});
  }

  // Remove player by socket
  removePlayer(socket){
    console.info(`Removing player [id=${socket.id}]`);

    // Remove the client
    this.#clients.delete(socket);
  }

  // Report to the game manager that the worker completed their share
  reportCompletedShare(socket, share){
    console.info(`Accepting share from [id=${socket.id}]`);
  }

  // Request a new chunk of work
  getNewShareOfWorkForWorker(socket){
    console.info(`Assigning new share to [id=${socket.id}]`);
  }

  // For the server to check if the game is over
  isGameOver(){
    return false;
  }

  // Restart the game with all the players still connected
  restartGameWithCurrentPlayers(){
    return this.#clients;
  }

  // Allow the server to retrieve a list of the clients
  getClients(){
    return this.#clients;
  }

}



