// 工作台/仪表盘页面
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { getUser, assetsAPI, budgetsAPI, messagesAPI } from '../utils/api';
import {
  Package,
  Wallet,
  Users,
  FileText,
  MessageSquare,
  TrendingUp,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { motion } from 'framer-motion';

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    assets: { total: 0, value: 0 },
    budgets: { total: 0, used: 0 },
    messages: { unread: 0 },
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentUser = getUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setUser(currentUser);
    fetchDashboardData();
  }, [navigate]);

  const fetchDashboardData = async () => {
    try {
      // 获取资产统计
      try {
        const assetStats = await assetsAPI.getStatistics();
        if (assetStats.code === 200) {
          setStats(prev => ({ ...prev, assets: assetStats.data || {} }));
        }
      } catch (e) {
        console.error('获取资产统计失败:', e);
      }

      // 获取预算统计
      try {
        const budgetStats = await budgetsAPI.getStatistics();
        if (budgetStats.code === 200) {
          setStats(prev => ({ ...prev, budgets: budgetStats.data || {} }));
        }
      } catch (e) {
        console.error('获取预算统计失败:', e);
      }

      // 获取未读消息
      try {
        if (user?.user_id) {
          const unreadResult = await messagesAPI.getUnreadCount(user.user_id);
          if (unreadResult.code === 200) {
            setStats(prev => ({ ...prev, messages: { unread: unreadResult.data?.count || 0 } }));
          }
        }
      } catch (e) {
        console.error('获取消息数失败:', e);
      }
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: '资产总数',
      value: stats.assets.total || 0,
      icon: Package,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-500',
      path: '/assets',
    },
    {
      title: '资产总值',
      value: `¥${((stats.assets.value || 0) / 10000).toFixed(1)}万`,
      icon: TrendingUp,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-500',
      path: '/assets',
    },
    {
      title: '预算总额',
      value: `¥${((stats.budgets.total || 0) / 10000).toFixed(1)}万`,
      icon: Wallet,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-500',
      path: '/budgets',
    },
    {
      title: '未读消息',
      value: stats.messages.unread || 0,
      icon: MessageSquare,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-500',
      path: '/messages',
    },
  ];

  const quickActions = [
    { icon: Package, label: '资产登记', path: '/assets', color: 'bg-blue-500' },
    { icon: Wallet, label: '预算申报', path: '/budgets', color: 'bg-orange-500' },
    { icon: FileText, label: '公文起草', path: '/documents', color: 'bg-green-500' },
    { icon: Users, label: '组织管理', path: '/organizations', color: 'bg-purple-500' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 欢迎标题 */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">欢迎回来，{user?.full_name || '用户'}</h1>
        <p className="text-primary-100">今天是您使用市政工程管理系统的第 天，祝您工作顺利</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => navigate(stat.path)}
              className="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-border"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.iconColor}`} />
                </div>
                <ArrowUpRight className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-muted-foreground text-sm mb-1">{stat.title}</p>
              <p className="text-2xl font-bold text-foreground">{stat.value}</p>
            </motion.div>
          );
        })}
      </div>

      {/* 快捷操作和公告 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 快捷操作 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
          <h2 className="text-lg font-semibold text-foreground mb-4">快捷操作</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.label}
                  onClick={() => navigate(action.path)}
                  className="flex flex-col items-center gap-2 p-4 rounded-xl hover:bg-muted transition-colors group"
                >
                  <div className={`p-3 rounded-full ${action.color} text-white group-hover:scale-110 transition-transform`}>
                    <Icon size={24} />
                  </div>
                  <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                    {action.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 系统公告 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-border">
          <h2 className="text-lg font-semibold text-foreground mb-4">系统公告</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-50">
              <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-foreground">系统升级通知</p>
                <p className="text-xs text-muted-foreground mt-1">系统将于本周六进行例行维护</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg bg-green-50">
              <MessageSquare className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-foreground">新功能上线</p>
                <p className="text-xs text-muted-foreground mt-1">资产统计功能已全面升级</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;