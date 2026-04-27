// 公文管理页面
import { useState, useEffect } from 'react';
import { getUser, documentsAPI } from '../utils/api';
import { FileText, Plus, Search, Edit, Trash2, X, Eye, Send } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function Documents() {
  const [user, setUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    doc_number: '',
    type: '通知',
    content: '',
    status: 'draft',
  });

  useEffect(() => {
    const currentUser = getUser();
    setUser(currentUser);
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await documentsAPI.getDocuments({ page: 1, page_size: 100 });
      if (response.code === 200) {
        setDocuments(response.data || []);
      }
    } catch (e) {
      console.error('获取公文失败:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedDoc) {
        await documentsAPI.updateDocument(selectedDoc.id, formData);
      } else {
        await documentsAPI.createDocument({
          ...formData,
          author_id: user?.user_id,
        });
      }
      fetchDocuments();
      closeModal();
    } catch (e) {
      alert('操作失败: ' + e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('确定要删除这篇公文吗？')) return;
    try {
      await documentsAPI.deleteDocument(id);
      fetchDocuments();
    } catch (e) {
      alert('删除失败: ' + e.message);
    }
  };

  const openModal = (doc = null) => {
    if (doc) {
      setSelectedDoc(doc);
      setFormData({
        title: doc.title || '',
        doc_number: doc.doc_number || '',
        type: doc.type || '通知',
        content: doc.content || '',
        status: doc.status || 'draft',
      });
    } else {
      setSelectedDoc(null);
      setFormData({
        title: '',
        doc_number: '',
        type: '通知',
        content: '',
        status: 'draft',
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedDoc(null);
  };

  const filteredDocs = documents.filter((doc) => {
    const matchSearch =
      doc.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.doc_number?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchStatus = !statusFilter || doc.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const statusOptions = [
    { value: 'draft', label: '草稿' },
    { value: 'pending', label: '待审批' },
    { value: 'approved', label: '已通过' },
    { value: 'rejected', label: '已驳回' },
  ];

  const typeOptions = ['通知', '公告', '决定', '批复', '报告', '函'];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">公文管理</h1>
          <p className="text-muted-foreground">管理公文收发和审批</p>
        </div>
        <button
          onClick={() => openModal()}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Plus size={20} />
          新增公文
        </button>
      </div>

      {/* 搜索和筛选 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-border">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
            <input
              type="text"
              placeholder="搜索公文标题或文号..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
          >
            <option value="">全部状态</option>
            {statusOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 公文列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">加载中...</div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <FileText size={48} className="mx-auto mb-4 opacity-50" />
            <p>暂无公文数据</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">公文标题</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">文号</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">类型</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">状态</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
                          <FileText className="w-5 h-5 text-green-500" />
                        </div>
                        <span className="font-medium text-foreground">{doc.title}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{doc.doc_number || '-'}</td>
                    <td className="px-4 py-3 text-muted-foreground">{doc.type}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                          doc.status === 'approved'
                            ? 'bg-green-50 text-green-600'
                            : doc.status === 'rejected'
                            ? 'bg-red-50 text-red-600'
                            : doc.status === 'pending'
                            ? 'bg-yellow-50 text-yellow-600'
                            : 'bg-gray-50 text-gray-600'
                        }`}
                      >
                        {statusOptions.find((s) => s.value === doc.status)?.label || doc.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openModal(doc)}
                          className="p-1.5 hover:bg-muted rounded-lg transition-colors"
                        >
                          <Edit size={16} className="text-muted-foreground" />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
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
              className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h2 className="text-lg font-semibold text-foreground">
                  {selectedDoc ? '编辑公文' : '新增公文'}
                </h2>
                <button onClick={closeModal} className="p-1 hover:bg-muted rounded-lg">
                  <X size={20} className="text-muted-foreground" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">公文标题 *</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">文号</label>
                    <input
                      type="text"
                      value={formData.doc_number}
                      onChange={(e) => setFormData({ ...formData, doc_number: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-1">公文类型</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                      className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                    >
                      {typeOptions.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">状态</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                  >
                    {statusOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">内容</label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    rows={6}
                    className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                    placeholder="请输入公文内容..."
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
                    {selectedDoc ? '保存修改' : '创建公文'}
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

export default Documents;