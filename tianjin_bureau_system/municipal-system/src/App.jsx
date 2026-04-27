// 主应用入口
import { Routes, Route, HashRouter as Router } from 'react-router';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Assets from './pages/Assets';
import Budgets from './pages/Budgets';
import Organizations from './pages/Organizations';
import Documents from './pages/Documents';
import Messages from './pages/Messages';
import MainLayout from './components/Layout';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="assets" element={<Assets />} />
          <Route path="budgets" element={<Budgets />} />
          <Route path="organizations" element={<Organizations />} />
          <Route path="documents" element={<Documents />} />
          <Route path="messages" element={<Messages />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;