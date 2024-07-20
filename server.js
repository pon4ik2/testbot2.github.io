// server.js
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const app = express();
const port = 3000;

// In-memory storage (replace with a database in production)
let users = {};

app.use(cors());
app.use(bodyParser.json());

// Endpoint to save user data
app.post('/saveUser', (req, res) => {
    const { id, username, score } = req.body;
    users[id] = { username, score };
    res.json({ success: true });
});

// Endpoint to get user data
app.get('/getUser/:id', (req, res) => {
    const id = req.params.id;
    if (users[id]) {
        res.json(users[id]);
    } else {
        res.json({ username: '', score: 0 });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});