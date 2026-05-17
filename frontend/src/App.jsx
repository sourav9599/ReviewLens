import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/shared/Layout'
import LandingPage from './pages/LandingPage'
import DashboardPage from './pages/DashboardPage'
import UploadPage from './pages/UploadPage'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#FFFFFF',
            color: '#1E293B',
            border: '1px solid #E5E7EB',
            fontFamily: 'Inter, DM Sans, sans-serif',
            fontSize: '14px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.1)',
          },
          success: { iconTheme: { primary: '#28C76F', secondary: '#FFFFFF' } },
          error:   { iconTheme: { primary: '#EA5455', secondary: '#FFFFFF' } },
        }}
      />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={<Layout />}>
          <Route path="/analyze" element={<UploadPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
