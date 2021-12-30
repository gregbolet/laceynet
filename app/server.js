const express = require('express');
//const WebSocket = require('ws');
const socketIO = require('socket.io');

const PORT = process.env.PORT || 5000;
const app = express();

// Serve all the files from the /public folder
// Given public/index.html it will be served from myaddress.com/index.html
app.use(express.static('public'))

const server = app.listen(PORT, function() {
	console.log(`Example app listening on port ${PORT}!`)
});

// socketIO will serve the websockets and handle reverse
// compatibility and fallback
const io = socketIO(server);

// This will map socketIDs (i.e: clients) to their assigned game numbers
// Example {socket object} => {nums: [2,3,4,5], currIdx: -1}
// Each new connection has a unique socket object
let clients = new Map();
let winningNum = -1;


function generate_all_player_nums(max_nums=10){
	let allnums = [];
	let temp = max_nums;

	// Create an array from 1 to max_nums
	for(;temp > 0; temp--){
		allnums.push(temp);
	}

	// Now have each client randomly grab numbers from the list
	let numsPerClient = Math.floor(max_nums/clients.size);

	// The value is the object with element data
	// Any modificaitons to clientData is done to the source object
	// The key is the socket object
	clients.forEach((clientData, socket) => {
		let myquota = numsPerClient;


		clientData.nums = [];

		for(;myquota > 0; myquota--){
			// remove an item at random from the list
			let randIdx = Math.floor(Math.random()*allnums.length);
			var val = allnums.splice(randIdx,1)[0];

			// Add the item to the list
			clientData.nums.push(val);
		}

		// Set the current index to 0
		clientData.currIdx = 0;
	});

	let leftoverNums = max_nums - (numsPerClient*clients.size);

	// Assign the leftover in roundrobin style
	clients.forEach((clientData, socket) => {

		if(leftoverNums > 0){
			leftoverNums--;

			clientData.nums.push(allnums[leftoverNums]);
		}
	});

	// Select a winning number
	winningNum = Math.floor(Math.random()*max_nums) + 1;
}

function restart_game(){
	// Regenerate the entire game
	generate_all_player_nums(10);

	console.log('New Player Data:');

	// Give all the connected clients the restart command
	clients.forEach((clientData, socket) => {
		socket.emit('command', {command:'restart', clientData});
		console.log(socket.id, clientData);
	});

}

io.on('connection', (socket) => {
	console.info(`Client connected [id=${socket.id}]`);

	// Add the client to the client list, keep their game info
	clients.set(socket, {nums: [], currIdx: -1});

	// Restart the game on a new connection
	restart_game();

	// Set the socket event handlers
	socket.on('disconnect', () => {
		console.log('Client disconnected');
		clients.delete(socket);
	});

	// Handle the event where the button was clicked
	socket.on('clicked', (msg) => {
		console.log(`playerid ${socket.id}, msg:`, msg);	

		// Update the client state and send it back to them
		// This update occurs to the client data object, not a copy of it
		let clientData = clients.get(socket);
		clientData.currIdx = clientData.currIdx + 1;

		// Send the client the updated information
		socket.emit('command', {command: 'update', clientData});
	});

});

// Update the page time every second
setInterval(() => {
	io.emit('time', new Date().toTimeString());
} , 1000);


