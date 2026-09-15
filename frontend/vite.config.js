import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forward /assistant, /shipments, /disruptions, /fleet, etc. to FastAPI
      '/assistant': 'http://localhost:8000',
      '/shipments': 'http://localhost:8000',
      '/disruptions': 'http://localhost:8000',
      '/fleet': 'http://localhost:8000',
      '/cold-chain-risk': 'http://localhost:8000',
      '/impacted-shipments': 'http://localhost:8000',
      '/simulate-disruption': 'http://localhost:8000',
      '/fleet-recommendation': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
