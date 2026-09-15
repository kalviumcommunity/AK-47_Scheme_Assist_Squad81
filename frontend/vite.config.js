import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const DB_PATH = path.resolve(__dirname, 'src/data/shared_db.json')

function readDb() {
  try {
    if (fs.existsSync(DB_PATH)) {
      return JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'))
    }
  } catch (err) {
    console.error('[shared-db] Failed to read database file:', err)
  }
  return { citizens: [], applications: [] }
}

function writeDb(data) {
  try {
    fs.mkdirSync(path.dirname(DB_PATH), { recursive: true })
    fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2), 'utf-8')
  } catch (err) {
    console.error('[shared-db] Failed to write database file:', err)
  }
}

function parseJsonBody(req) {
  return new Promise((resolve, reject) => {
    let body = ''
    req.on('data', chunk => { body += chunk })
    req.on('end', () => {
      if (!body) return resolve({})
      try {
        resolve(JSON.parse(body))
      } catch (err) {
        reject(err)
      }
    })
    req.on('error', reject)
  })
}

function sharedDataPlugin() {
  return {
    name: 'schemeassist-shared-data-server',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        // Set CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*')
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS')
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

        if (req.method === 'OPTIONS') {
          res.statusCode = 200
          res.end()
          return
        }

        const url = req.url ? req.url.split('?')[0] : ''

        // ─── CITIZENS ENDPOINTS ─────────────────────────────
        if (url === '/api-shared/citizens') {
          const db = readDb()
          if (!Array.isArray(db.citizens)) db.citizens = []

          if (req.method === 'GET') {
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify(db.citizens))
            return
          }

          if (req.method === 'POST') {
            try {
              const citizen = await parseJsonBody(req)
              if (citizen && (citizen.email || citizen.id || citizen.name)) {
                const key = (citizen.email || citizen.id || citizen.name).toLowerCase().trim()
                const existingIndex = db.citizens.findIndex(c =>
                  (c.email && c.email.toLowerCase() === key) ||
                  (c.id && c.id.toLowerCase() === key) ||
                  (c.name && c.name.toLowerCase() === key)
                )

                if (existingIndex >= 0) {
                  db.citizens[existingIndex] = {
                    ...db.citizens[existingIndex],
                    ...citizen,
                    lastLoginAt: new Date().toISOString()
                  }
                } else {
                  db.citizens.push({
                    id: citizen.id || `CIT-${Math.floor(100000 + Math.random() * 900000)}`,
                    name: citizen.name || 'Citizen',
                    email: citizen.email || '',
                    phone: citizen.phone || '',
                    state: citizen.state || 'Not provided',
                    role: 'citizen',
                    registeredAt: citizen.registeredAt || new Date().toISOString(),
                    lastLoginAt: new Date().toISOString(),
                    status: citizen.status || 'Active',
                    ...citizen
                  })
                }
                writeDb(db)
                res.setHeader('Content-Type', 'application/json')
                res.end(JSON.stringify({ success: true, citizen }))
                return
              }
            } catch (e) {
              res.statusCode = 400
              res.end(JSON.stringify({ error: 'Invalid JSON payload' }))
              return
            }
          }
        }

        // ─── APPLICATIONS ENDPOINTS ─────────────────────────
        if (url === '/api-shared/applications') {
          const db = readDb()
          if (!Array.isArray(db.applications)) db.applications = []

          if (req.method === 'GET') {
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify(db.applications))
            return
          }

          if (req.method === 'POST') {
            try {
              const newApp = await parseJsonBody(req)
              if (newApp) {
                // Prepend new application
                db.applications = [newApp, ...db.applications.filter(a => a.id !== newApp.id)]

                // Also make sure applicant citizen is recorded in citizens list
                if (newApp.citizenEmail || newApp.citizenName || newApp.citizenId) {
                  const applicantKey = (newApp.citizenEmail || newApp.citizenId || newApp.citizenName).toLowerCase().trim()
                  const citizenExists = (db.citizens || []).some(c =>
                    (c.email && c.email.toLowerCase() === applicantKey) ||
                    (c.id && c.id.toLowerCase() === applicantKey)
                  )
                  if (!citizenExists) {
                    if (!Array.isArray(db.citizens)) db.citizens = []
                    db.citizens.push({
                      id: newApp.citizenId || `CIT-${Math.floor(100000 + Math.random() * 900000)}`,
                      name: newApp.citizenName || 'Citizen',
                      email: newApp.citizenEmail || '',
                      phone: newApp.phone || '',
                      state: newApp.state || 'Not provided',
                      role: 'citizen',
                      registeredAt: new Date().toISOString(),
                      lastLoginAt: new Date().toISOString(),
                      status: 'Active'
                    })
                  }
                }

                writeDb(db)
                res.setHeader('Content-Type', 'application/json')
                res.end(JSON.stringify({ success: true, application: newApp }))
                return
              }
            } catch (e) {
              res.statusCode = 400
              res.end(JSON.stringify({ error: 'Invalid JSON payload' }))
              return
            }
          }
        }

        // ─── UPDATE APPLICATION STATUS ──────────────────────
        if (url.startsWith('/api-shared/applications/') && req.method === 'PATCH') {
          const appId = url.split('/api-shared/applications/')[1]
          try {
            const body = await parseJsonBody(req)
            const db = readDb()
            const app = (db.applications || []).find(a => a.id === appId)
            if (app) {
              app.status = body.status || app.status
              app.statusCode = (body.status || app.status).toLowerCase().replace(/\s+/g, '_')
              app.reviewedAt = new Date().toISOString()
              if (Array.isArray(app.timeline)) {
                app.timeline = app.timeline.map((stage, idx) => ({
                  ...stage,
                  done: body.status === 'Approved' ? true : idx === 0 || stage.done,
                  date: idx === 2 && body.status !== 'Under Review' ? new Date().toISOString().split('T')[0] : stage.date
                }))
              }
              writeDb(db)
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ success: true, application: app }))
              return
            } else {
              res.statusCode = 404
              res.end(JSON.stringify({ error: 'Application not found' }))
              return
            }
          } catch (e) {
            res.statusCode = 400
            res.end(JSON.stringify({ error: 'Failed to update application' }))
            return
          }
        }

        // ─── USER DOCUMENTS ENDPOINTS ───────────────────────
        if (url === '/api-shared/documents') {
          const db = readDb()
          if (!Array.isArray(db.userDocuments)) db.userDocuments = []

          if (req.method === 'GET') {
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify(db.userDocuments))
            return
          }

          if (req.method === 'POST') {
            try {
              const doc = await parseJsonBody(req)
              if (doc && (doc.filename || doc.name)) {
                db.userDocuments = [
                  doc,
                  ...db.userDocuments.filter(d => d.filename !== doc.filename && d.id !== doc.id)
                ]
                writeDb(db)
                res.setHeader('Content-Type', 'application/json')
                res.end(JSON.stringify({ success: true, document: doc }))
                return
              }
            } catch (e) {
              res.statusCode = 400
              res.end(JSON.stringify({ error: 'Invalid document payload' }))
              return
            }
          }
        }

        if (url.startsWith('/api-shared/documents/') && req.method === 'DELETE') {
          const docIdOrName = decodeURIComponent(url.split('/api-shared/documents/')[1])
          const db = readDb()
          if (!Array.isArray(db.userDocuments)) db.userDocuments = []
          db.userDocuments = db.userDocuments.filter(d => d.filename !== docIdOrName && d.id !== docIdOrName)
          writeDb(db)
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ success: true }))
          return
        }

        next()
      })
    }
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), sharedDataPlugin()],
  server: {
    port: 3000,
    open: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
