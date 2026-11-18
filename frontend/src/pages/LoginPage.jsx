import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();

  const simularLogin = () => {
    localStorage.setItem('token', 'token-prueba-navegacion');
    navigate('/dashboard');
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Inicio de Sesión</h1>
      <p>Estructura base lista para maquetar en el siguiente issue.</p>
      <button onClick={simularLogin}>Simular acceso al panel</button>
    </div>
  );
}

export default LoginPage;