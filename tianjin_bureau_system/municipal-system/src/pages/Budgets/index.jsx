// 预算管理页面
import { useState, useEffect } from 'react';
import { getUser, budgetsAPI } from '../utils/api';
import { Wallet, Plus, Search, Edit, Trash2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function Budgets() {
  const [user, setUser] = useState(null);
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    year: new Date().getFullYear(),
    total_amount: 0,
    used_amount: 0,
    category: '',
    department: '',
  });

  useEffect(() => {
    const currentUser = getUser();
    setUser(currentUser);
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      const response = await budgetsAPI.getBudgets({ page: 1, page_size: 100 });
      if (response.code === 200) {
        setBudgets(response.data || []);
      }
    } catch (e) {
      console.error('获取预算失败:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedBudget) {
        await budgetsAPI.updateBudget(selectedBudget.id, formData);
      } else {
        await budgetsAPI.createBudget(formData);
      }
      fetchBudgets();
      closeModal();
    } catch (e) {
      alert('操作失败: ' + e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这条预算记录吗？')) return;
    try {
      await budgetsAPI.deleteBudget(id);
      fetchBudgets();
    } catch (e) {
      alert('删除失败: ' + e.message);
    }
  };

  const openModal = (budget = null) => {
    if (budget) {
      setSelectedBudget(budget);
      setFormData({
        name: budget.name || '',
        year: budget.year || new Date().getFullYear(),
        total_amount: budget.total_amount || 0,
        used_amount: budget.used_amount || 0,
        category: budget.category || '',
        department: budget.department || '',
      });
    } else {
      setSelectedBudget(null);
      setFormData({
        name: '',
        year: new Date().getFullYear(),
        total_amount: 0,
        used_amount: 0,
        category: '',
        department: '',
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedBudget(null);
  };

  const filteredBudgets = budgets.filter(
    (budget) =>
      budget.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      budget.department?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalBudget = budgets.reduce((sum, b) => sum + (b.total_amount || 0), 0);
  const totalUsed = budgets.reduce((sum, b) => sum + (b.used_amount || 0), 0);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">预算管理</h1>
          <p className="text-muted-foreground">管理预算资金使用情况</p>
        </div>
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus size={20} />
          新增预算
        </button>
      </div>

      {/* 预算概览 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-border">
          <p className="text-muted-foreground text-sm mb-1">预算总额</p>
          <p className="text-2xl font-bold text-foreground">¥{totalBudget.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-border">
          <p className="text-muted-foreground text-sm mb-1">已使用</p>
          <p className="text-2xl font-bold text-orange-500">¥{totalUsed.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-border">
          <p className="text-muted-foreground text-sm mb-1">剩余可用</p>
          <p className="text-2xl font-bold text-green-500">
            ¥{(totalBudget - totalUsed).toLocaleString()}
          </p>
        </div>
      </div>

      {/* 搜索 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
          <input
            type="text"
            placeholder="搜索预算名称或部门..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          />
        </div>
      </div>

      {/* 预算列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">加载中...</div>
        ) : filteredBudgets.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <Wallet size={48} className="mx-auto mb-4 opacity-50" />
            <p>暂无预算数据</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">预算名称</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">年度</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">部门</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">预算总额</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">已使用</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">使用率</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredBudgets.map((budget) => {
                  const usageRate = budget.total_amount ? (budget.used_amount / budget.total_amount) * 100 : 0;
                  return (
                    <tr key={budget.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-4 py-3 font-medium text-foreground">{budget.name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{budget.year}</td>
                      <td className="px-4 py-3 text-muted-foreground">{budget.department || '-'}</td>
                      <td className="px-4 py-3 text-foreground">¥{budget.total_amount?.toLocaleString()}</td>
                      <td className="px-4 py-3 text-orange-500">¥{budget.used_amount?.toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                usageRate > 90 ? 'bg-red-500' : usageRate > 70 ? 'bg-orange-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(usageRate, 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-muted-foreground">{usageRate.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => openModal(budget)}
                            className="p-1.5 hover:bg-muted rounded-lg transition-colors"
                          >
                            <Edit size={16} className="text-muted-foreground" />
                          </button>
                          <button
                            onClick={() => handleDelete(budget.id)}
                            className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 size={16} className="text-red-500" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 弹窗 */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-lg"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h2 className="text-lg font-semibold text-foreground">
                  {selectedBudget ? '编辑预算' : '新增预算'}
                </h2>
                <button onClick={closeModal} className="p-1 hover:bg-muted rounded-lg">
                  <X size={20} className="text-muted-foreground" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">预算名称 *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">年度 *</label>
                    <input
                      type="number"
                      value={formData.year}
                      onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">预算总额 *</label>
                    <input
                      type="number"
                      value={formData.total_amount}
                      onChange={(e) => setFormData({ ...formData, total_amount: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">部门</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                  >
                    {selectedBudget ? '保存修改' : '创建预算'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default Budgets;