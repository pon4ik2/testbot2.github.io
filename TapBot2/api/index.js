const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();

// In-memory storage (replace with a database in production)
let users = {};

app.use(cors());
app.use(bodyParser.json());

// Middleware to log all incoming requests
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} request to ${req.url}`);
    next();
});

app.post('/api/saveUser', (req, res) => {
    console.log('Received POST request to /api/saveUser');
    console.log('Request body:', req.body);

    try {
        const { id, username, score, lastClickTime, referrer } = req.body;
        
        if (!id || !username || score === undefined || lastClickTime === undefined) {
            console.error('Invalid data received');
            return res.status(400).json({ success: false, error: 'Invalid data' });
        }

        if (!users[id]) {
            // New user
            users[id] = { username, score, lastClickTime, referrals: [] };
            
            // If there's a referrer, add bonus and update referrer's data
            if (referrer && users[referrer]) {
                users[referrer].score += 50; // Add 50 coins to referrer
                users[referrer].referrals.push(id);
            }
        } else {
            // Existing user, update data
            users[id].username = username;
            users[id].score = score;
            users[id].lastClickTime = lastClickTime;
        }

        console.log('Updated users object:', users);

        res.json({ success: true });
    } catch (error) {
        console.error('Error in /api/saveUser:', error);
        res.status(500).json({ success: false, error: 'Internal server error' });
    }
});

app.get('/api/getUser/:id', (req, res) => {
    console.log('Received GET request to /api/getUser/:id');
    
    const id = req.params.id;
    console.log('Requested user ID:', id);

    try {
        if (users[id]) {
            console.log('User found:', users[id]);
            res.json(users[id]);
        } else {
            console.log('User not found, returning default data');
            res.json({ username: '', score: 0, lastClickTime: 0, referrals: [] });
        }
    } catch (error) {
        console.error('Error in /api/getUser:', error);
        res.status(500).json({ success: false, error: 'Internal server error' });
    }
});

// Root route for testing
app.get('/', (req, res) => {
    res.json({ message: 'API is working' });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('An error occurred:', err);
    res.status(500).json({ success: false, error: 'Internal server error' });
});

module.exports = app;
