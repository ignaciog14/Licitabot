import { NavLink } from "react-router-dom";

export default function Layout({ children }) {
  const linkClass = ({ isActive }) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? "bg-talinay-dark text-white"
        : "text-blue-100 hover:bg-talinay-dark hover:text-white"
    }`;

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-talinay shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-8">
              <span className="text-xl font-bold text-white">
                Talinay Compras
              </span>
              <div className="flex gap-2">
                <NavLink to="/" end className={linkClass}>
                  Bandeja
                </NavLink>
                <NavLink to="/historial" className={linkClass}>
                  Historial
                </NavLink>
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
