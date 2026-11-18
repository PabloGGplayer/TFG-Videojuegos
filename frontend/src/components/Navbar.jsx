import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav style={{ display: 'flex', gap: '1.5rem', padding: '1rem 2rem', background: '#1e293b', color: '#fff', alignItems: 'center' }}>
      <strong>Plataforma B2B TFG</strong>
      <Link to="/dashboard" style={{ color: '#e2e8f0', textDecoration: 'none' }}>Panel & Analítica</Link>
      <Link to="/catalogo" style={{ color: '#e2e8f0', textDecoration: 'none' }}>Catálogo de Juegos</Link>
      <Link to="/empresa" style={{ color: '#e2e8f0', textDecoration: 'none' }}>Gestión de Empresa</Link>
      <button
        onClick={handleLogout}
        style={{ marginLeft: 'auto', padding: '0.4rem 0.8rem', cursor: 'pointer', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px' }}
      >
        Cerrar sesión
      </button>
    </nav>
  );
}

export default Navbar;