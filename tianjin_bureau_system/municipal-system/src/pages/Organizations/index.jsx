// 组织管理页面
import { useState, useEffect } from 'react';
import { getUser, organizationsAPI } from '../utils/api';
import { Users, Plus, Search, Edit, Trash2, X, Building2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function Organizations() {
  const [user, setUser] = useState(null);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    type: 'department',
    parent_id: null,
    contact: '',
    phone: '',
  });

  useEffect(() => {
    const currentUser = getUser();
    setUser(currentUser);
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      const response = await organizationsAPI.getOrganizations({ page: 1, page_size: 100 });
      if (response.code === 200) {
        setOrganizations(response.data || []);
      }
    } catch (e) {
      console.error('获取组织失败:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedOrg) {
        await organizationsAPI.updateOrganization(selectedOrg.id, formData);
      } else {
        await organizationsAPI.createOrganization(formData);
      }
      fetchOrganizations();
      closeModal();
    } catch (e) {
      alert('操作失败: ' + e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这个组织吗？')) return;
    try {
      await organizationsAPI.deleteOrganization(id);
      fetchOrganizations();
    } catch (e) {
      alert('删除失败: ' + e.message);
    }
  };

  const openModal = (org = null) => {
    if (org) {
      setSelectedOrg(org);
      setFormData({
        name: org.name || '',
        code: org.code || '',
        type: org.type || 'department',
        parent_id: org.parent_id || null,
        contact: org.contact || '',
        phone: org.phone || '',
      });
    } else {
      setSelectedOrg(null);
      setFormData({
        name: '',
        code: '',
        type: 'department',
        parent_id: null,
        contact: '',
        phone: '',
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedOrg(null);
  };

  const filteredOrgs = organizations.filter(
    (org) =>
      org.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      org.code?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const typeOptions = [
    { value: 'department', label: '局机关' },
    { value: 'unit', label: '中层单位' },
    { value: 'sub_unit', label: '基层单位' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">组织管理</h1>
          <p className="text-muted-foreground">管理组织架构和部门信息</p>
        </div>
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus size={20} />
          新增组织
        </button>
      </div>

      {/* 搜索 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
          <input
            type="text"
            placeholder="搜索组织名称或编码..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          />
        </div>
      </div>

      {/* 组织列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">加载中...</div>
        ) : filteredOrgs.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <Users size={48} className="mx-auto mb-4 opacity-50" />
            <p>暂无组织数据</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">组织名称</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">编码</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">类型</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">联系人</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">电话</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredOrgs.map((org) => (
                  <tr key={org.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-secondary-50 flex items-center justify-center">
                          <Building2 className="w-5 h-5 text-secondary-500" />
                        </div>
                        <span className="font-medium text-foreground">{org.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{org.code || '-'}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                          org.type === 'department'
                            ? 'bg-primary-50 text-primary-600'
                            : org.type === 'unit'
                            ? 'bg-secondary-50 text-secondary-600'
                            : 'bg-accent-50 text-accent-600'
                        }`}
                      >
                        {typeOptions.find((t) => t.value === org.type)?.label || org.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{org.contact || '-'}</td>
                    <td className="px-4 py-3 text-muted-foreground">{org.phone || '-'}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openModal(org)}
                          className="p-1.5 hover:bg-muted rounded-lg transition-colors"
                        >
                          <Edit size={16} className="text-muted-foreground" />
                        </button>
                        <button
                          onClick={() => handleDelete(org.id)}
                          className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 size={16} className="text-red-500" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
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
                  {selectedOrg ? '编辑组织' : '新增组织'}
                </h2>
                <button onClick={closeModal} className="p-1 hover:bg-muted rounded-lg">
                  <X size={20} className="text-muted-foreground" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">组织名称 *</label>
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
                    <label className="block text-sm font-medium text-foreground mb-1">组织编码</label>
                    <input
                      type="text"
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">组织类型</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    >
                      {typeOptions.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">联系人</label>
                  <input
                    type="text"
                    value={formData.contact}
                    onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">联系电话</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
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
                    {selectedOrg ? '保存修改' : '创建组织'}
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

export default Organizations;