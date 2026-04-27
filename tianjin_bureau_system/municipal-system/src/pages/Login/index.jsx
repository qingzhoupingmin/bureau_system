// 登录页面
import { useState } from 'react';
import { useNavigate } from 'react-router';
import { authAPI } from '../utils/api';
import { Building2 } from 'lucide-react';

function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(username, password);

      if (response.code === 200) {
        // 保存用户信息到 localStorage
        localStorage.setItem('token', 'authenticated');
        localStorage.setItem('user', JSON.stringify(response.data));
        navigate('/');
      }
    } catch (err) {
      setError(err.message || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1569172122301-bc5008bc09c5?w=1920')] bg-cover bg-center opacity-10"></div>

      <div className="relative w-full max-w-md px-4">
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 animate-scale-in border border-white/50">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 shadow-lg mb-4">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">天津市市政工程局</h1>
            <p className="text-muted-foreground mt-1">综合管理系统</p>
          </div>

          {/* 登录表单 */}
          <form onSubmit={handleLogin} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm animate-fade-in">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">用户名</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-border bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
                placeholder="请输入用户名"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-border bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all outline-none"
                placeholder="请输入密码"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>提示: 请使用系统账号登录</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;