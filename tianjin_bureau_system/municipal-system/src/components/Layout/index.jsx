// 主布局组件
import { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router';
import { getUser, authAPI } from '../utils/api';
import {
  Building2,
  LayoutDashboard,
  Package,
  Wallet,
  Users,
  FileText,
  MessageSquare,
  LogOut,
  Menu,
  X,
  Bell,
} from 'lucide-react';

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: '工作台' },
  { path: '/assets', icon: Package, label: '资产管理' },
  { path: '/budgets', icon: Wallet, label: '预算管理' },
  { path: '/organizations', icon: Users, label: '组织管理' },
  { path: '/documents', icon: FileText, label: '公文管理' },
  { path: '/messages', icon: MessageSquare, label: '消息中心' },
];

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const currentUser = getUser();
    if (!currentUser) {
      navigate('/login');
    } else {
      setUser(currentUser);
    }
  }, [navigate]);

  const handleLogout = async () => {
    try {
      if (user?.user_id) {
        await authAPI.logout(user.user_id);
      }
    } catch (e) {
      console.error('登出错误:', e);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/login');
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-muted">
      {/* 顶部导航栏 */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-border z-50 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-foreground">天津市市政工程局</h1>
              <p className="text-xs text-muted-foreground">综合管理系统</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-muted rounded-lg transition-colors relative">
            <Bell size={20} className="text-muted-foreground" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <div className="flex items-center gap-3 pl-4 border-l border-border">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-foreground">{user.full_name}</p>
              <p className="text-xs text-muted-foreground">{user.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-red-50 text-muted-foreground hover:text-red-500 rounded-lg transition-colors"
              title="退出登录"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* 侧边栏 */}
      <aside
        className={`fixed top-16 left-0 h-[calc(100vh-4rem)] bg-white border-r border-border transition-all duration-300 z-40
          ${sidebarOpen ? 'w-64' : 'w-16'}
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        <div className="flex flex-col h-full">
          {/* 收起/展开按钮 */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden lg:flex items-center justify-center h-10 border-b border-border hover:bg-muted transition-colors"
          >
            <Menu size={18} className="text-muted-foreground" />
          </button>

          {/* 菜单项 */}
          <nav className="flex-1 p-2 overflow-y-auto">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    navigate(item.path);
                    setMobileOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg mb-1 transition-all
                    ${isActive
                      ? 'bg-primary-50 text-primary-600 font-medium'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                >
                  <Icon size={20} />
                  <span className={`${sidebarOpen ? 'block' : 'hidden'} whitespace-nowrap`}>
                    {item.label}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      </aside>

      {/* 移动端遮罩 */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setMobileOpen(false)}
        ></div>
      )}

      {/* 主内容区 */}
      <main
        className={`pt-16 min-h-screen transition-all duration-300 ${
          sidebarOpen ? 'lg:ml-64' : 'lg:ml-16'
        }`}
      >
        <div className="p-4 lg:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default MainLayout;