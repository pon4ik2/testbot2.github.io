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

    const { id, username, score } = req.body;
    
    if (!id || !username || score === undefined) {
        console.error('Invalid data received');
        return res.status(400).json({ success: false, error: 'Invalid data' });
    }

    users[id] = { username, score };
    console.log('Updated users object:', users);

    res.json({ success: true });
});

app.get('/api/getUser/:id', (req, res) => {
    console.log('Received GET request to /api/getUser/:id');
    
    const id = req.params.id;
    console.log('Requested user ID:', id);

    if (users[id]) {
        console.log('User found:', users[id]);
        res.json(users[id]);
    } else {
        console.log('User not found, returning default data');
        res.json({ username: '', score: 0 });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('An error occurred:', err);
    res.status(500).json({ success: false, error: 'Internal server error' });
});

// If you're using Vercel, you need to export the app
module.exports = app;

// If you're running this directly (not on Vercel), uncomment these lines:
// const PORT = process.env.PORT || 3000;
// app.listen(PORT, () => {
//     console.log(`Server is running on port ${PORT}`);
// });
