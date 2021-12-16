const express = require('express')
const path = require('path')
const PORT = process.env.PORT || 5000
const cookieParser = require('cookie-parser')
const cors = require('cors');
const bodyParser = require('body-parser');
const concat = require('concat-stream');
const qs = require('querystring');

const app = express()

app.use(cors());
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')))

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'ejs')


const refreshRate = 1000; // in milliseconds
let clients = [];
let clientDict = {};
let clientPositions = {};
let winningNum = -1;
let facts = [];
let weGotAWinner = false;
let winnerId = -1;

app.get('/', (req, res) => {
	res.render('pages/index');
	//res.send('pages/index');
});


function generate_all_player_nums(max_nums=10){

	let allnums = [];

	let temp = max_nums;

	// Create an array from 1 to max_nums
	for(;temp > 0; temp--){
		allnums.push(temp);
	}

	// Now have each client randomly grab numbers from the list
	let numsPerClient = Math.floor(max_nums/clients.length);

	clients.forEach(client => {
		const clientId = client.id;
		let myquota = numsPerClient;

		clientDict[clientId] = [];

		for(;myquota > 0; myquota--){
			// remove an item at random from the list
			let randIdx = Math.floor(Math.random()*allnums.length);
			var val = allnums.splice(randIdx,1)[0];

			// Add the item to the list
			clientDict[clientId].push(val);
		}


		clientPositions[clientId] = 0;
	});

	let leftoverNums = max_nums - (numsPerClient*clients.length);

	// Assign the leftover in roundrobin style
	clients.forEach(client => {
		
		if(leftoverNums > 0){
			const clientId = client.id;
			leftoverNums--;

			clientDict[clientId].push(allnums[leftoverNums]);
		}
	});

	winningNum = Math.floor(Math.random()*max_nums) + 1;
}

// For each client, generate an array of numbers
function restart_game(){
	generate_all_player_nums(10);

	clients.forEach(client => {
		const clientId = client.id;

		// For this client, tell them to write restarting text
		const data = JSON.stringify({"clientId":`${clientId}`, "command":'restart'});
		const message = `retry: ${refreshRate}\nid:${clientId}\ndata: ${data}\n\n`;
		client.response.write(message);
	})

	console.log('Restarting game!');
	console.log(clientDict);
	console.log(clientPositions);
	console.log(winningNum);
}

// When someone accesses the /events page, they will use the Server-Sent Events API
function eventsHandler(request, response, next) {

	const headers = {
		'Content-Type': 'text/event-stream',
		'Connection': 'keep-alive',
		'Cache-Control': 'no-cache'
	};

	// Arrival time is the assigned client ID
	const clientId = Date.now();

	// keep the response object around to be able to notify all workers/clients
	const newClient = {
		id: clientId,
		response
	};

	// Add the client to the client list
	clients.push(newClient);

	// Upon closing the connection, we remove the client
	request.on('close', () => {
		console.log(`${clientId} Connection closed`);
		delete clientDict[clientId];
		delete clientPositions[clientId];
		clients = clients.filter(client => client.id !== clientId);
		restart_game();
	});


	// Expire 1 day from now
	const cookieExpiry = 24 * 60 * 60 * 1000;
	//console.log(req.cookies['workerId'])

	// Give them a cookie if they don't have one
	response.cookie(`workerID`,`${clientId}`,{
		maxAge: cookieExpiry,
		// expires works the same as the maxAge
		expires: clientId + cookieExpiry, 
		secure: true,
		httpOnly: true,
		path: '/',
		sameSite: 'lax'
	});

	response.writeHead(200, headers);

	// Now that we added the new client, let's regenerate the game
	restart_game();

	
	// Every second, send update data
//	return setInterval(() => {
//		const id = Date.now();
//		const data = `ID-by-Time: ${id} ID-for-game:${newClient.id}`;
//		const message = `retry: ${refreshRate}\nid:${id}\ndata: ${data}\n\n`;
//		response.write(message);
//	}, refreshRate);
	
	return;
}

app.get('/events', eventsHandler);


app.post('/', (req, resp) => {

	var data = req.body;
	var clientId = data.clientId;
	console.log(data);

	// This is the only registered event we have for the game rn
	if(data.buttonevent == 'press'){
		// get the numbers for this client
		var clientNums = clientDict[clientId];
		var currPos = clientPositions[clientId];

		var dataToSend;
		var message;

		// If we advance the winner button, restart the game
		if(weGotAWinner && winnerId == clientId){

			weGotAWinner = false;
			winnerId = -1;

			restart_game();
			resp.sendStatus(200);
			return;
		}

		// Check if the last element was a winner
		else if((currPos-1 >= 0) && clientNums[currPos-1] == winningNum){

			weGotAWinner = true;
			winnerId = clientId;

			// For this client, notify them that they're a winner! 
			dataToSend = JSON.stringify({"clientId":`${clientId}`, 
						     "command":'winner'});
			message = `id:${clientId}\ndata: ${dataToSend}\n\n`;

			clients.forEach(client => {
				if(client.id == clientId){
					client.response.write(message);
				}
			});


			// Tell everyone the game is over
			clients.forEach(client => {
				// For this client, tell them to write restarting text
				dataToSend = JSON.stringify({"clientId":`${client.id}`, 
							     "command":'gameover'});
				message = `id:${client.id}\ndata: ${dataToSend}\n\n`;

				if(client.id != clientId){
					client.response.write(message);
				}
			});

			// exit
			resp.sendStatus(200);
			return;

		}
		// If we finished our numbers, it's game over for us
		else if(clientNums.length <= currPos){
			// For this client, tell them to write restarting text
			dataToSend = JSON.stringify({"clientId":`${clientId}`, 
						     "command":'gameover'});
			message = `id:${clientId}\ndata: ${dataToSend}\n\n`;
		}
		else{
			// get the next number on their list
			var nextNum = clientNums[currPos];

			// For this client, tell them to continue playing 
			dataToSend = JSON.stringify({"clientId":`${clientId}`, 
						     "command":'continue', 
						     "nextnum": nextNum});
			message = `id:${clientId}\ndata: ${dataToSend}\n\n`;

			// advance their number
			clientPositions[clientId] = clientPositions[clientId] + 1;
		}


		clients.forEach(client => {
			if(client.id == clientId){
				client.response.write(message);
			}
		});

	}

	resp.sendStatus(200);
});

// Serve any static files form the public folder
app.use('/static', express.static('public'))

app.listen(PORT, () => console.log(`Listening on ${ PORT }`))
