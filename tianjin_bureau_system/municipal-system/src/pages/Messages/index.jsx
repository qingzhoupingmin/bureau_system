// 消息中心页面
import { useState, useEffect } from 'react';
import { getUser, messagesAPI } from '../utils/api';
import { MessageSquare, Search, Check, CheckCheck, Trash2, Send } from 'lucide-react';
import { motion } from 'framer-motion';

function Messages() {
  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [showSendModal, setShowSendModal] = useState(false);
  const [formData, setFormData] = useState({
    receiver_id: '',
    title: '',
    content: '',
  });

  useEffect(() => {
    const currentUser = getUser();
    setUser(currentUser);
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await messagesAPI.getMessages({ page: 1, page_size: 100 });
      if (response.code === 200) {
        setMessages(response.data || []);
      }
    } catch (e) {
      console.error('获取消息失败:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (messageId) => {
    try {
      await messagesAPI.markAsRead(messageId);
      fetchMessages();
    } catch (e) {
      console.error('标记已读失败:', e);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    try {
      await messagesAPI.sendMessage({
        ...formData,
        sender_id: user?.user_id,
      });
      fetchMessages();
      setShowSendModal(false);
      setFormData({ receiver_id: '', title: '', content: '' });
      alert('消息发送成功');
    } catch (e) {
      alert('发送失败: ' + e.message);
    }
  };

  const filteredMessages = messages.filter(
    (msg) =>
      msg.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      msg.content?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const unreadCount = messages.filter((m) => !m.is_read).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">消息中心</h1>
          <p className="text-muted-foreground">
            {unreadCount > 0 ? `您有 ${unreadCount} 条未读消息` : '暂无未读消息'}
          </p>
        </div>
        <button
          onClick={() => setShowSendModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Send size={20} />
          发送消息
        </button>
      </div>

      {/* 搜索 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-border">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
          <input
            type="text"
            placeholder="搜索消息标题或内容..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          />
        </div>
      </div>

      {/* 消息列表 */}
      <div className="bg-white rounded-xl shadow-sm border border-border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">加载中...</div>
        ) : filteredMessages.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
            <p>暂无消息</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {filteredMessages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className={`p-4 hover:bg-muted/50 cursor-pointer transition-colors ${
                  !message.is_read ? 'bg-blue-50/50' : ''
                }`}
                onClick={() => {
                  setSelectedMessage(message);
                  if (!message.is_read) {
                    handleMarkAsRead(message.id);
                  }
                }}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.is_read ? 'bg-muted' : 'bg-primary-100'
                    }`}
                  >
                    <MessageSquare
                      size={20}
                      className={message.is_read ? 'text-muted-foreground' : 'text-primary-600'}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <h3
                        className={`font-medium truncate ${
                          message.is_read ? 'text-muted-foreground' : 'text-foreground'
                        }`}
                      >
                        {message.title}
                      </h3>
                      <span className="text-xs text-muted-foreground flex-shrink-0">
                        {message.created_at || message.send_time}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground truncate">{message.content}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {!message.is_read && (
                      <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* 消息详情弹窗 */}
      {selectedMessage && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedMessage(null)}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-2xl shadow-xl w-full max-w-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">{selectedMessage.title}</h2>
              <p className="text-sm text-muted-foreground mt-1">
                {selectedMessage.sender_name || selectedMessage.sender_id} · {selectedMessage.created_at}
              </p>
            </div>
            <div className="p-4">
              <p className="text-foreground whitespace-pre-wrap">{selectedMessage.content}</p>
            </div>
            <div className="flex justify-end gap-3 p-4 border-t border-border">
              <button
                onClick={() => setSelectedMessage(null)}
                className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                关闭
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* 发送消息弹窗 */}
      {showSendModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowSendModal(false)}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-2xl shadow-xl w-full max-w-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">发送消息</h2>
            </div>
            <form onSubmit={handleSend} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">接收人 ID</label>
                <input
                  type="number"
                  value={formData.receiver_id}
                  onChange={(e) => setFormData({ ...formData, receiver_id: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">消息标题 *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">消息内容 *</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  rows={4}
                  className="w-full px-4 py-2 rounded-lg border border-border focus:ring-2 focus:ring-primary-500 outline-none resize-none"
                  required
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowSendModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  发送
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}

export default Messages;