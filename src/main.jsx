import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './hooks/useAuth'
import AppContent from './App'
import LandingPage from './components/LandingPage'
import ChatPage from './components/ChatPage'
import Dashboard from './components/Dashboard'
import Settings from './components/Settings'

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppContent />,
  },
  {
    path: "/landing", 
    element: <LandingPage />,
  },
  {
    path: "/chat",
    element: <ChatPage />,
  },
  {
    path: "/dashboard",
    element: <Dashboard />,
  },
  {
    path: "/settings",
    element: <Settings />,
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
