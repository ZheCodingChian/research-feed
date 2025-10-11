import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LandingPage } from './pages/LandingPage'
import { ExplorerPage } from './pages/ExplorerPage'
import { PaperDetails } from './pages/PaperDetails'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/explorer" element={<ExplorerPage />} />
        <Route path="/paper/:id" element={<PaperDetails />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App