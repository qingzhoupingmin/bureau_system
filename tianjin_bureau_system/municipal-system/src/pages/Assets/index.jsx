// 资产管理页面
import { useState, useEffect } from 'react';
import { getUser, assetsAPI } from '../utils/api';
import {
  Package,
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Eye,
  X,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function Assets() {
  const [user, setUser] = useState(null);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    model: '',
    serial_number: '',
    price: 0,
    location: '',
    status: 'normal',
    caretaker: '',
  });

  useEffect(() => {
    const currentUser = getUser();
    setUser(currentUser);
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await assetsAPI.getAssets({ page: 1, page_size: 100 });
      if (response.code === 200) {
        setAssets(response.data || []);
      }
    } catch (e) {
      console.error('获取资产失败:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedAsset) {
        await assetsAPI.updateAsset(selectedAsset.id, formData);
      } else {
        await assetsAPI.createAsset({
          ...formData,
          organization_id: user?.organization_id,
        });
      }
      fetchAssets();
      closeModal();
    } catch (e) {
      alert('操作失败: ' + e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这条资产记录吗？')) return;
    try {
      await assetsAPI.deleteAsset(id);
      fetchAssets();
    } catch (e) {
      alert('删除失败: ' + e.message);
    }
  };

  const openModal = (asset = null) => {
    if (asset) {
      setSelectedAsset(asset);
      setFormData({
        name: asset.name || '',
        category: asset.category || '',
        model: asset.model || '',
        serial_number: asset.serial_number || '',
        price: asset.price || 0,
        location: asset.location || '',
        status: asset.status || 'normal',
        caretaker: asset.caretaker || '',
      });
    } else {
      setSelectedAsset(null);
      setFormData({
        name: '',
        category: '',
        model: '',
        serial_number: '',
        price: 0,
        location: '',
        status: 'normal',
        caretaker: '',
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedAsset(null);
  };

  const filteredAssets = assets.filter((asset) => {
    const matchSearch =
      asset.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.serial_number?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCategory = !categoryFilter || asset.category === categoryFilter;
    return matchSearch && matchCategory;
  });

  const categories = [...new Set(assets.map((a) => a.category).filter(Boolean))];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">资产管理</h1>
          <p className="text-muted-foreground">管理您的资产信息</p>
        </div>
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus size={20} />
          新增资产
        </button>
      </div>

      {/* 搜索和筛选 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-border">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
            <input
              type="text"
              placeholder="搜索资产名称或编号..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-muted-foreground" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
            >
              <option value="">全部类别</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 资产列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">加载中...</div>
        ) : filteredAssets.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <Package size={48} className="mx-auto mb-4 opacity-50" />
            <p>暂无资产数据</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">资产名称</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">类别</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">编号</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">价值</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">位置</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">状态</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredAssets.map((asset) => (
                  <tr key={asset.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                          <Package className="w-5 h-5 text-primary-500" />
                        </div>
                        <span className="font-medium text-foreground">{asset.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{asset.category || '-'}</td>
                    <td className="px-4 py-3 text-muted-foreground">{asset.serial_number || '-'}</td>
                    <td className="px-4 py-3 text-foreground">¥{asset.price?.toLocaleString()}</td>
                    <td className="px-4 py-3 text-muted-foreground">{asset.location || '-'}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                          asset.status === 'normal'
                            ? 'bg-green-50 text-green-600'
                            : asset.status === 'maintenance'
                            ? 'bg-yellow-50 text-yellow-600'
                            : 'bg-red-50 text-red-600'
                        }`}
                      >
                        {asset.status === 'normal' ? (
                          <CheckCircle size={12} />
                        ) : (
                          <XCircle size={12} />
                        )}
                        {asset.status === 'normal' ? '正常' : asset.status === 'maintenance' ? '维护中' : '报废'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openModal(asset)}
                          className="p-1.5 hover:bg-muted rounded-lg transition-colors"
                          title="编辑"
                        >
                          <Edit size={16} className="text-muted-foreground" />
                        </button>
                        <button
                          onClick={() => handleDelete(asset.id)}
                          className="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                          title="删除"
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

      {/* 资产表单弹窗 */}
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
              className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h2 className="text-lg font-semibold text-foreground">
                  {selectedAsset ? '编辑资产' : '新增资产'}
                </h2>
                <button onClick={closeModal} className="p-1 hover:bg-muted rounded-lg">
                  <X size={20} className="text-muted-foreground" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">资产名称 *</label>
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
                    <label className="block text-sm font-medium text-foreground mb-1">类别 *</label>
                    <input
                      type="text"
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">资产编号</label>
                    <input
                      type="text"
                      value={formData.serial_number}
                      onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">型号</label>
                    <input
                      type="text"
                      value={formData.model}
                      onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">价值 (元) *</label>
                    <input
                      type="number"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">位置</label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">状态</label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    >
                      <option value="normal">正常</option>
                      <option value="maintenance">维护中</option>
                      <option value="scrapped">报废</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">保管人</label>
                  <input
                    type="text"
                    value={formData.caretaker}
                    onChange={(e) => setFormData({ ...formData, caretaker: e.target.value })}
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
                    {selectedAsset ? '保存修改' : '创建资产'}
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

export default Assets;