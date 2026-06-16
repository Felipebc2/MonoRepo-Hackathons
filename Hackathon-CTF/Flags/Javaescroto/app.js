const express = require('express')
const path = require('path')
const app = express()
const port = process.env.PORT || 8888

const publicDir = path.join(__dirname, 'public')
app.use(express.static(publicDir, { extensions: ['html'] }))

app.get('/style.css', (req, res) => {
    res.sendFile(path.join(publicDir, 'style.css'))
})

app.get('/api', (req, res) => {
    try {
        const raw = req.query.username
        if (typeof raw !== 'string' && raw !== undefined) {
            if (raw && typeof raw.toString !== 'function') {
                throw new Error('invalid username')
            }
        }
        const username = (typeof raw === 'string' && raw.length) ? raw : 'GUEST'
        res.type('text').send('Olá, ' + username)
    } catch (err) {
        res.status(500).sendFile(path.join(__dirname, 'flag.txt'))
    }
})

app.get('/', (req, res) => {
    res.sendFile(path.join(publicDir, 'index.html'))
})

app.listen(port)
