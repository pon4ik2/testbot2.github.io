const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();

// In-memory storage (replace with a database in production)
let users = {};

app.use(cors());
app.use(bodyParser.json());

app.post('/api/saveUser', (req, res) => {
    const { id, username, score } = req.body;
    users[id] = { username, score };
    res.json({ success: true });
});

app.get('/api/getUser/:id', (req, res) => {
    const id = req.params.id;
    if (users[id]) {
        res.json(users[id]);
    } else {
        res.json({ username: '', score: 0 });
    }
});

module.exports = app;