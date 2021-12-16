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

app.get('/', (req, res) => {


	res.render('pages/index');
	//res.send('pages/index');
});

// For each client, generate an array of numbers
function restart_game(){
	clients.forEach(client => {
		const clientId = client.id;

		clientDict[clientId] = [0,1,2,3,4,5];
		clientPositions[clientId] = 0;

		// For this client, tell them to write restarting text
		const data = JSON.stringify({"clientId":`${clientId}`, "command":'restart'});
		const message = `retry: ${refreshRate}\nid:${clientId}\ndata: ${data}\n\n`;
		client.response.write(message);
	})

	winningNum = 4;

	console.log('Restarting game!');
	console.log(clientDict);
	console.log(clientPositions);
}

// When someone accesses the /events page, they will use the Server-Sent Events API
function eventsHandler(request, response, next) {

	const headers = {
		'Content-Type': 'text/event-stream',
		'Connection': 'keep-alive',
		'Cache-Control': 'no-cache'
	};

	//const data = `data: ${JSON.stringify(facts)}\n\n`;

	// Keep the response object open, when they refresh the page, close it
	// This means that on each refresh, it's acting like a new player
	//response.write('blah blah');
	//response.setStatus(200);

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

	if(data.buttonevent == 'press'){
		// get the numbers for this client
		var clientNums = clientDict[clientId];
		var currPos = clientPositions[clientId];

		var dataToSend;
		var message;

		// If we finished our numbers, it's game over for us
		if(clientNums.length <= currPos){
			// For this client, tell them to write restarting text
			dataToSend = JSON.stringify({"clientId":`${clientId}`, 
						     "command":'gameover'});
			message = `id:${clientId}\ndata: ${dataToSend}\n\n`;
		}
		else{
			// get the next number on their list
			var nextNum = clientNums[clientPositions[clientId]];

			// advance their number
			clientPositions[clientId] = clientPositions[clientId] + 1;


			// For this client, tell them to write restarting text
			dataToSend = JSON.stringify({"clientId":`${clientId}`, 
						     "command":'continue', 
						     "nextnum": nextNum});
			message = `id:${clientId}\ndata: ${dataToSend}\n\n`;

			//clients[clientId].response.write(message);
		}


		clients.forEach(client => {
			if(client.id == clientId){
				client.response.write(message);
			}
		});

	}

	resp.sendStatus(200);
});

app.listen(PORT, () => console.log(`Listening on ${ PORT }`))
