
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
export class GameManager{

  // Let's set up the game to play
  constructor(maxNums, workChunkSize){
    console.log('Starting new game...');

    // Setup the game. This means the client list
    // and the problem space for the clients to explore
    this.#maxNums = maxNums;
    this.#workChunkSize = workChunkSize;
    this.#clients = new Map();
    this.#allShares = [];

    let allNums = [];

    // Create an array from 1 to maxNums
    // This will be our global problem
    for(;maxNums > 0; maxNums--){
      allnums.push(temp);
    }

    // Now let's create shares of this entire space


    // Select a winning number
    this.#winningNum = Math.floor(Math.random()*maxNums) + 1;

    console.log('New game started.');
  }


  // Add a player to the game, needs to be by socket
  // as the socket is the identifier
  addPlayer(socket){
	  console.info(`Adding player [id=${socket.id}]`);

    // Map the socket to its assigned chunks
    this.#clients.set(socket, {currentShare:[], acceptedShares:[]});
  }

  // Remove player by socket
  removePlayer(socket){
	  console.info(`Removing player [id=${socket.id}]`);

    // Remove the client
		this.#clients.delete(socket);
  }

  reportCompletedShare(socket, share){
	  console.info(`Accepting share from [id=${socket.id}]`);
  }

  

}
