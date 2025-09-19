import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'
import './index.css'
import LandingPage from './components/LandingPage'
import ChatPage from './components/ChatPage'
import Dashboard from './components/Dashboard'
import History from './components/History'

const router = createBrowserRouter([
  {
    path: "/",
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
    path: "history",
    element: <History />,
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
