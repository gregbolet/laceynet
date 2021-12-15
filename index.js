const cool = require('cool-ascii-faces')
const express = require('express')
const path = require('path')
const PORT = process.env.PORT || 5000
const cookieParser = require('cookie-parser')

const app = express()

app.use(express.static(path.join(__dirname, 'public')))
app.use(cookieParser());

app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'ejs')
app.get('/', (req, res) => res.render('pages/index'))
app.get('/cool', (req, res) => res.send(cool()))

app.get('/cookieLand', (req,res) => {
	res.send('my simple http server');
})

//a get route for adding a cookie

app.get('/setcookie', (req, res) => {
	res.cookie(`Cookie token name`,`encrypted cookie string Value`,{
		maxAge: 5000,
		// expires works the same as the maxAge
		expires: new Date('01 12 2021'),
		secure: true,
		httpOnly: true,
		sameSite: 'lax'
	});
	res.send('Cookie have been saved successfully');
});

// get the cookie incoming request
app.get('/getcookie', (req, res) => {
	//show the saved cookies
	console.log(req.cookies)
	res.send(req.cookies);
});


app.listen(PORT, () => console.log(`Listening on ${ PORT }`))
