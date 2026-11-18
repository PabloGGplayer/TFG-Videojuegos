import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CatalogPage from './pages/CatalogPage';
import CompanyAdminPage from './pages/CompanyAdminPage';

function PrivateLayout({ children }) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta pública */}
        <Route path="/login" element={<LoginPage />} />

        {/* Rutas protegidas (requieren sesión activa) */}
        <Route element={<ProtectedRoute />}>
          <Route
            path="/dashboard"
            element={
              <PrivateLayout>
                <DashboardPage />
              </PrivateLayout>
            }
          />
          <Route
            path="/catalogo"
            element={
              <PrivateLayout>
                <CatalogPage />
              </PrivateLayout>
            }
          />
          <Route
            path="/empresa"
            element={
              <PrivateLayout>
                <CompanyAdminPage />
              </PrivateLayout>
            }
          />
        </Route>

        {/* Redirección por defecto */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;