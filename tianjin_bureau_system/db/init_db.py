# -*- coding: utf-8 -*-
"""
数据库初始化模块 - 直接连接不使用单例
"""
from config import DEPARTMENTS, ORG_TYPE_DEPARTMENT, ORG_TYPE_UNIT, ORG_TYPE_SUB_UNIT, DB_CONFIG, SUB_UNITS_BRIDGE, SUB_UNITS_HIGHWAY, SUB_UNITS_HIGHWAY_EXPRESS, SUB_UNITS_DESIGN, SUB_UNITS_METRO, SUB_UNITS_RESEARCH, SUB_UNITS_CONSTRUCTION
import pymysql


def get_db_connection():
    """获取数据库连接 - 使用配置文件"""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )


def init_database():
    """初始化数据库和表结构"""
    # 先创建数据库 - 使用配置文件
    init_conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )
    with init_conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS tianjin_bureau CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    init_conn.commit()
    init_conn.close()

    conn = get_db_connection()

    # 创建组织表
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizations (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            type ENUM('department', 'unit', 'leader') NOT NULL,
            parent_id INT NULL,
            sort_order INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_type (type),
            INDEX idx_parent (parent_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            organization_id INT NOT NULL,
            full_name VARCHAR(50),
            position VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_role (role),
            INDEX idx_org (organization_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            sub_category VARCHAR(50),
            model VARCHAR(100),
            serial_number VARCHAR(100),
            purchase_date DATE,
            price DECIMAL(12,2),
            location VARCHAR(100),
            status VARCHAR(20) DEFAULT 'normal',
            organization_id INT,
            is_public TINYINT DEFAULT 0,
            caretaker VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_category (category),
            INDEX idx_org (organization_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_applications (
            id INT PRIMARY KEY AUTO_INCREMENT,
            asset_id INT NOT NULL,
            applicant_id INT NOT NULL,
            applicant_org_id INT NOT NULL,
            reason TEXT,
            apply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending',
            approver_id INT,
            approve_date DATETIME,
            approve_comment TEXT,
            INDEX idx_asset (asset_id),
            INDEX idx_applicant (applicant_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumables (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            unit VARCHAR(10),
            stock INT DEFAULT 0,
            min_stock INT DEFAULT 10,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumable_records (
            id INT PRIMARY KEY AUTO_INCREMENT,
            consumable_id INT NOT NULL,
            user_id INT NOT NULL,
            organization_id INT NOT NULL,
            quantity INT NOT NULL,
            record_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_consumable (consumable_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            doc_type VARCHAR(20),
            sender_id INT NOT NULL,
            sender_org_id INT NOT NULL,
            receiver_org_ids VARCHAR(200),
            is_official TINYINT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'draft',
            create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            publish_date DATETIME,
            INDEX idx_sender (sender_id),
            INDEX idx_status (status),
            INDEX idx_type (doc_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            sender_id INT NOT NULL,
            sender_org_id INT NOT NULL,
            receiver_org_id INT,
            message_type VARCHAR(20) DEFAULT 'business',
            is_public TINYINT DEFAULT 0,
            create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_sender (sender_id),
            INDEX idx_type (message_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_replies (
            id INT PRIMARY KEY AUTO_INCREMENT,
            message_id INT NOT NULL,
            reply_user_id INT NOT NULL,
            reply_org_id INT NOT NULL,
            content TEXT,
            reply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_message (message_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_projects (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            applicant_id INT NOT NULL,
            applicant_org_id INT NOT NULL,
            budget DECIMAL(12,2),
            status VARCHAR(20) DEFAULT 'pending',
            apply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            approve_date DATETIME,
            approver_id INT,
            approve_comment TEXT,
            INDEX idx_applicant (applicant_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_funds (
            id INT PRIMARY KEY AUTO_INCREMENT,
            project_id INT NOT NULL,
            total_budget DECIMAL(12,2),
            allocated DECIMAL(12,2) DEFAULT 0,
            used DECIMAL(12,2) DEFAULT 0,
            create_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_project (project_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget_applications (
            id INT PRIMARY KEY AUTO_INCREMENT,
            organization_id INT NOT NULL,
            year INT NOT NULL,
            amount DECIMAL(12,2),
            purpose TEXT,
            type VARCHAR(20),
            status VARCHAR(20) DEFAULT 'pending',
            apply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            approver_id INT,
            approve_date DATETIME,
            approve_comment TEXT,
            INDEX idx_org (organization_id),
            INDEX idx_year (year),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS leadership_positions (
            id INT PRIMARY KEY AUTO_INCREMENT,
            position_title VARCHAR(50) NOT NULL,
            user_id INT,
            managed_departments VARCHAR(200),
            managed_units VARCHAR(200),
            responsibilities TEXT,
            start_date DATE,
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            action VARCHAR(100),
            table_name VARCHAR(50),
            record_id INT,
            ip_address VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_action (action)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            username VARCHAR(50),
            ip_address VARCHAR(50),
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME,
            status VARCHAR(20),
            INDEX idx_user (user_id),
            INDEX idx_login_time (login_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # 创建密码修改申请表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_change_applications (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            username VARCHAR(50) NOT NULL,
            old_password VARCHAR(255) NOT NULL,
            new_password VARCHAR(255) NOT NULL,
            reason TEXT,
            apply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'pending',
            approver_id INT,
            approve_date DATETIME,
            approve_comment TEXT,
            INDEX idx_user (user_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

    conn.commit()
    conn.close()
    print("数据库表创建完成！")


def init_organization_data():
    """初始化组织数据"""
    conn = get_db_connection()

    # 检查是否已有数据
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as cnt FROM organizations")
        result = cursor.fetchone()
        if result['cnt'] > 0:
            print("组织数据已存在，跳过初始化")
            conn.close()
            return

        # 插入处室数据
        for dept_id, dept_name in DEPARTMENTS.items():
            cursor.execute("INSERT INTO organizations (id, name, type, sort_order) VALUES (%s, %s, %s, %s)",
                        (dept_id, dept_name, ORG_TYPE_DEPARTMENT, dept_id))

        # 插入下属单位数据
        units = [
            (21, '天津市公路处', 21),
            (22, '天津市高速公路管理处', 22),
            (23, '天津市道路桥梁管理处', 23),
            (24, '天津市市政工程经济技术定额研究站（天津市公路工程定额管理站）', 24),
            (25, '天津市市政工程配套办公室', 25),
            (26, '天津市市政工程研究院（天津市公路工程研究院）', 26),
            (27, '天津市市政工程设计研究院', 27),
            (28, '天津市市政工程学校', 28),
            (29, '天津市市政公路管理局干部中等专业学校（中国共产党天津市市政公路管理局委员会党校）', 29),
            (30, '天津市市政公路管理局技工学校', 30),
            (31, '天津市市政工程建设公司（天津市市政公路利用世界银行贷款办公室）', 31),
            (32, '天津市贷款道路建设车辆通行费征收办公室', 32),
            (33, '天津市贷款道路建设车辆通行费稽查管理处', 33),
            (34, '天津市公路养路费征稽处', 34),
            (35, '天津市公路养护工程处', 35),
            (36, '天津市乡村公路管理办公室', 36),
            (37, '天津市市政公路工程质量监督站（天津市公路工程质量安全监督站）', 37),
            (38, '天津市地铁管理处', 38),
            (39, '天津市市政公路信息中心', 39),
            (40, '天津市市政公路行业管理办公室', 40),
        ]
        for unit_id, unit_name, sort_order in units:
            cursor.execute("INSERT INTO organizations (id, name, type, sort_order) VALUES (%s, %s, %s, %s)",
                        (unit_id, unit_name, ORG_TYPE_UNIT, sort_order))

        # 插入道路桥梁处下属单位（ID 51-60）
        for sub_id, sub_name in SUB_UNITS_BRIDGE.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 23, sub_id))

        # 插入公路处下属单位（ID 81-85）
        for sub_id, sub_name in SUB_UNITS_HIGHWAY.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 21, sub_id))

        # 插入高速处下属单位（ID 61-72）
        for sub_id, sub_name in SUB_UNITS_HIGHWAY_EXPRESS.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 22, sub_id))

        # 插入设计院下属单位（ID 62）
        for sub_id, sub_name in SUB_UNITS_DESIGN.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 27, sub_id))

        # 插入研究院下属单位（ID 73-79）
        for sub_id, sub_name in SUB_UNITS_RESEARCH.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 26, sub_id))

        # 插入建设公司下属单位（ID 86-88）
        for sub_id, sub_name in SUB_UNITS_CONSTRUCTION.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 31, sub_id))

        # 插入地铁处下属单位（ID 63）
        for sub_id, sub_name in SUB_UNITS_METRO.items():
            cursor.execute("INSERT INTO organizations (id, name, type, parent_id, sort_order) VALUES (%s, %s, %s, %s, %s)",
                        (sub_id, sub_name, ORG_TYPE_SUB_UNIT, 38, sub_id))

    conn.commit()
    conn.close()
    print("组织数据初始化完成！")


def init_default_users():
    """初始化所有处室、单位、领导的默认用户"""
    import hashlib
    from config import DEPARTMENTS

    def hash_pwd(password):
        return hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        result = cursor.fetchone()
        if result['cnt'] > 0:
            # 清空旧用户重新初始化
            cursor.execute("DELETE FROM users")
            conn.commit()
            print(f"已清空旧用户数据: {result['cnt']} 条")

        # 1. 系统管理员 (1个)
        default_users = [
            ('admin', hash_pwd('admin123'), 'system_admin', 0, '系统管理员'),
        ]

        # 2. 19个处室，每个处室2个账号
        # 账号格式：处室简称+数字，例如 科技处1、科技处2
        # 密码格式：处室简称+123，例如 科技处123
        dept_users = [
            # 办公室 (1)
            ('办公室1', '办公室123', 'office_staff', 1, '办公室-账号1'),
            ('办公室2', '办公室123', 'office_staff', 1, '办公室-账号2'),
            # 计划处 (2)
            ('计划处1', '计划处123', 'normal_user', 2, '计划处-账号1'),
            ('计划处2', '计划处123', 'normal_user', 2, '计划处-账号2'),
            # 设施管理处 (3)
            ('设施管理处1', '设施管理处123', 'normal_user', 3, '设施管理处-账号1'),
            ('设施管理处2', '设施管理处123', 'normal_user', 3, '设施管理处-账号2'),
            # 设施养护处 (4)
            ('设施养护处1', '设施养护处123', 'normal_user', 4, '设施养护处-账号1'),
            ('设施养护处2', '设施养护处123', 'normal_user', 4, '设施养护处-账号2'),
            # 建设管理处 (5)
            ('建设管理处1', '建设管理处123', 'normal_user', 5, '建设管理处-账号1'),
            ('建设管理处2', '建设管理处123', 'normal_user', 5, '建设管理处-账号2'),
            # 规划处 (6)
            ('规划处1', '规划处123', 'normal_user', 6, '规划处-账号1'),
            ('规划处2', '规划处123', 'normal_user', 6, '规划处-账号2'),
            # 财务处 (7)
            ('财务处1', '财务处123', 'finance_staff', 7, '财务处-账号1'),
            ('财务处2', '财务处123', 'finance_staff', 7, '财务处-账号2'),
            # 规费管理处 (8)
            ('规费管理处1', '规费管理处123', 'normal_user', 8, '规费管理处-账号1'),
            ('规费管理处2', '规费管理处123', 'normal_user', 8, '规费管理处-账号2'),
            # 审计处 (9)
            ('审计处1', '审计处123', 'normal_user', 9, '审计处-账号1'),
            ('审计处2', '审计处123', 'normal_user', 9, '审计处-账号2'),
            # 资产管理处 (10)
            ('资产管理处1', '资产管理处123', 'asset_manager', 10, '资产管理处-账号1'),
            ('资产管理处2', '资产管理处123', 'asset_manager', 10, '资产管理处-账号2'),
            # 劳动人事处 (11)
            ('劳动人事处1', '劳动人事处123', 'normal_user', 11, '劳动人事处-账号1'),
            ('劳动人事处2', '劳动人事处123', 'normal_user', 11, '劳动人事处-账号2'),
            # 科技处 (12)
            ('科技处1', '科技处123', 'tech_staff', 12, '科技处-账号1'),
            ('科技处2', '科技处123', 'tech_staff', 12, '科技处-账号2'),
            # 安全保卫处 (13)
            ('安全保卫处1', '安全保卫处123', 'normal_user', 13, '安全保卫处-账号1'),
            ('安全保卫处2', '安全保卫处123', 'normal_user', 13, '安全保卫处-账号2'),
            # 法规处 (14)
            ('法规处1', '法规处123', 'normal_user', 14, '法规处-账号1'),
            ('法规处2', '法规处123', 'normal_user', 14, '法规处-账号2'),
            # 党委办公室 (15)
            ('党委办公室1', '党委办公室123', 'normal_user', 15, '党委办公室-账号1'),
            ('党委办公室2', '党委办公室123', 'normal_user', 15, '党委办公室-账号2'),
            # 纪检委 (16)
            ('纪检委1', '纪检委123', 'normal_user', 16, '纪检委-账号1'),
            ('纪检委2', '纪检委123', 'normal_user', 16, '纪检委-账号2'),
            # 宣传部 (17)
            ('宣传部1', '宣传部123', 'normal_user', 17, '宣传部-账号1'),
            ('宣传部2', '宣传部123', 'normal_user', 17, '宣传部-账号2'),
            # 组织部 (18)
            ('组织部1', '组织部123', 'normal_user', 18, '组织部-账号1'),
            ('组织部2', '组织部123', 'normal_user', 18, '组织部-账号2'),
            # 老干部处 (19)
            ('老干部处1', '老干部处123', 'normal_user', 19, '老干部处-账号1'),
            ('老干部处2', '老干部处123', 'normal_user', 19, '老干部处-账号2'),
        ]
        default_users.extend(dept_users)

        # 3. 20个下属单位，每个单位2个账号
        # 账号格式：单位简称+数字，例如 公路处1、公路处2
        # 密码格式：单位简称+123，例如 公路处123
        unit_users = [
            (21, '公路处'), (22, '高速处'), (23, '桥管处'),
            (24, '定额站'), (25, '配套办'), (26, '研究院'),
            (27, '设计院'), (28, '市政学校'), (29, '干校'),
            (30, '技校'), (31, '建设公司'), (32, '征收办'),
            (33, '稽查办'), (34, '征稽处'), (35, '养护处'),
            (36, '乡村办'), (37, '质监站'), (38, '地铁处'),
            (39, '信息中心'), (40, '行业办'),
        ]
        for unit_id, unit_name in unit_users:
            unit_pwd = f'{unit_name}123'
            default_users.append((f'{unit_name}1', unit_pwd, 'unit_user', unit_id, f'{unit_name}-账号1'))
            default_users.append((f'{unit_name}2', unit_pwd, 'unit_user', unit_id, f'{unit_name}-账号2'))

# 3.5 道路桥梁处下属单位账号（每个单位2个账号）
        sub_unit_users = [
            (51, '一桥所'), (52, '二桥所'), (53, '一道所'),
            (54, '二道所'), (55, '一快路所'), (56, '二快路所'),
            (57, '拌合厂'), (58, '机修厂'), (59, '监理所'), (60, '广告部'),
        ]
        for sub_id, sub_name in sub_unit_users:
            sub_pwd = f'{sub_name}123'
            default_users.append((f'{sub_name}1', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号1'))
            default_users.append((f'{sub_name}2', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号2'))

        # 3.5.1 公路处下属单位账号（5个单位，每个2个账号）
        highway_sub_units = [
            (81, '一公管所'), (82, '二公管所'), (83, '三公管所'),
            (84, '四公管所'), (85, '外环公路'),
        ]
        for sub_id, sub_name in highway_sub_units:
            sub_pwd = f'{sub_name}123'
            default_users.append((f'{sub_name}1', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号1'))
            default_users.append((f'{sub_name}2', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号2'))

        # 3.6 高速处下属单位账号（10个单位，每个2个账号）
        highway_express_sub_units = [
            (61, '收费中心'), (64, '一路政'), (65, '二路政'),
            (66, '三路政'), (67, '四路政'), (68, '监控中心'),
            (69, '一养护'), (70, '二养护'), (71, '三养护'), (72, '四养护'),
        ]
        for sub_id, sub_name in highway_express_sub_units:
            sub_pwd = f'{sub_name}123'
            default_users.append((f'{sub_name}1', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号1'))
            default_users.append((f'{sub_name}2', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号2'))

        # 3.6 高速处下属单位账号（10个单位，每个2个账号）
        highway_sub_units = [
            (61, '收费中心'), (64, '一路政'), (65, '二路政'),
            (66, '三路政'), (67, '四路政'), (68, '监控中心'),
            (69, '一养护'), (70, '二养护'), (71, '三养护'), (72, '四养护'),
        ]
        for sub_id, sub_name in highway_sub_units:
            sub_pwd = f'{sub_name}123'
            default_users.append((f'{sub_name}1', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号1'))
            default_users.append((f'{sub_name}2', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号2'))

        # 3.7 设计院下属单位账号（1个单位2个账号）
        default_users.append(('城市分院1', '城市分院123', 'sub_unit_user', 62, '城市分院-账号1'))
        default_users.append(('城市分院2', '城市分院123', 'sub_unit_user', 62, '城市分院-账号2'))

        # 3.8 研究院下属单位账号（7个单位，每个2个账号）
        research_sub_units = [
            (73, '质检中心'), (74, '路桥检测'), (75, '海顺设计'),
            (76, '建达科技'), (77, '路驰监理'), (78, '金艾检测'), (79, '滨海分院'),
        ]
        for sub_id, sub_name in research_sub_units:
            sub_pwd = f'{sub_name}123'
            default_users.append((f'{sub_name}1', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号1'))
            default_users.append((f'{sub_name}2', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号2'))

        # 3.9 建设公司下属单位账号（3个单位，每个2个账号）
        construction_sub_units = [
            (86, '道桥建设'), (87, '道桥建筑'), (88, '道桥工程'),
        ]
        for sub_id, sub_name in construction_sub_units:
            sub_pwd = f'{sub_name}123'
            default_users.append((f'{sub_name}1', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号1'))
            default_users.append((f'{sub_name}2', sub_pwd, 'sub_unit_user', sub_id, f'{sub_name}-账号2'))

        # 3.10 地铁处下属单位账号（1个单位2个账号）
        default_users.append(('地铁总公司1', '地铁总公司123', 'sub_unit_user', 63, '地铁总公司-账号1'))
        default_users.append(('地铁总公司2', '地铁总公司123', 'sub_unit_user', 63, '地铁总公司-账号2'))

        # 4. 领导职务，每个1个账号
        # 账号格式：职务简称+数字
        # 密码格式：职务简称+123
        leader_users = [
            ('党委书记1', '党委书记123', 'leader', 0, '党委书记'),
            ('局长1', '局长123', 'leader', 0, '党委副书记、局长'),
            ('副局长1', '副局长123', 'leader', 0, '党委副书记、副局长'),
            ('副局长2', '副局长123', 'leader', 0, '党委副书记'),
            ('参事1', '参事123', 'leader', 0, '市人民政府参事'),
            ('纪委书记1', '纪委书记123', 'leader', 0, '党委常委、纪委书记'),
            ('常委1', '常委123', 'leader', 0, '党委常委、副局长'),
            ('常委2', '常委123', 'leader', 0, '党委常委、副局长'),
            ('总工程师1', '总工程师123', 'leader', 0, '总工程师'),
            ('总经济师1', '总经济师123', 'leader', 0, '总经济师'),
        ]
        default_users.extend(leader_users)

        # 插入所有用户
        inserted_count = 0
        for username, password, role, org_id, full_name in default_users:
            try:
                cursor.execute("INSERT INTO users (username, password, role, organization_id, full_name) VALUES (%s, %s, %s, %s, %s)",
                              (username, hash_pwd(password), role, org_id, full_name))
                inserted_count += 1
            except Exception as e:
                print(f"  插入用户 {username} 失败: {e}")

    conn.commit()
    conn.close()
    print(f"默认用户初始化完成！共 {inserted_count}/{len(default_users)} 个账号")
    print(f"  - 系统管理员: admin / admin123")
    print(f"  - 局领导: secretary / leader123")
    print(f"  - 办公室: office_1 / office123")


def init_all():
    """初始化所有数据"""
    print("开始初始化数据库...")
    init_database()
    init_organization_data()
    init_default_users()
    print("初始化完成！")


if __name__ == '__main__':
    init_all()