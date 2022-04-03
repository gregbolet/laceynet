module.export = class DisplayManager{

	static displayIo;

	constructor(displayIo){
		this.displayIo = displayIo;

		this.displayIo.on('connection', (socket) => { DisplayManager.displayOnConnectHandler(socket); });
	}

	static displayOnConnectHandler(socket){
		  console.info(`display Client connected [id=${socket.id}]`);
	
		  //initial registration
		  let clientMapping = Object.fromEntries(clientDict);
		  let params = GameMan.getParams();
		  let winLedger = GameMan.getLedger();
		  console.log(winningClient);
		  socket.emit('displayRegistered', {map: clientMapping, parameters: params, isGameOver: GameMan.getIsGameOver(), winner: winningClient, ledger: winLedger});
	
	
	
		  socket.on('disconnect', () => {
		    console.log('display Client disconnected');
		  });
	}


}