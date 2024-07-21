const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');

const app = express();

app.use(cors());
app.use(bodyParser.json());

const USERS_FILE = "/tmp/users.json";

function loadUsers() {
    if (fs.existsSync(USERS_FILE)) {
        return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
    }
    return {};
}

function saveUsers(users) {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users));
}

app.post('/api/saveUser', (req, res) => {
    console.log('Received POST request to /api/saveUser');
    console.log('Request body:', req.body);

    try {
        const { id, username, points, lastClickTime, referrals, referrer } = req.body;
        
        if (!id || !username || points === undefined || !lastClickTime) {
            console.error('Invalid data received');
            return res.status(400).json({ success: false, error: 'Invalid data' });
        }

        let users = loadUsers();
        const isNewUser = !users[id];
        users[id] = { username, points, lastClickTime, referrals, referrer };
        saveUsers(users);

        res.json({ success: true, isNewUser });
    } catch (error) {
        console.error('Error in /api/saveUser:', error);
        res.status(500).json({ success: false, error: 'Internal server error' });
    }
});

app.get('/api/getUser/:id', (req, res) => {
    console.log('Received GET request to /api/getUser/:id');
    
    const id = req.params.id;
    console.log('
