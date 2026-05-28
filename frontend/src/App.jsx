import { Routes, Route } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Bandeja from "./pages/Bandeja.jsx";
import Configuracion from "./pages/Configuracion.jsx";
import Detalle from "./pages/Detalle.jsx";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Bandeja />} />
        <Route path="/oportunidad/:id" element={<Detalle />} />
        <Route path="/configuracion" element={<Configuracion />} />
      </Routes>
    </Layout>
  );
}
