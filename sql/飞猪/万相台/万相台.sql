-- =========================================
-- 万相台
-- 文件: 万相台.xlsx
-- =========================================
USE feizhu;

CREATE TABLE IF NOT EXISTS fliggy_wanxiangtai (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    date_time DATE NOT NULL COMMENT 'Date 时间',
    cost DECIMAL(14,2) COMMENT 'Cost 花费',
    imp BIGINT COMMENT 'IMP 观看量',
    click INT COMMENT 'Click 点击',
    order_count INT COMMENT 'Order 订单',
    sales DECIMAL(14,2) COMMENT 'Sales 销量',
    shopping_cart INT COMMENT 'ShoppingCart 加入购物车',
    bookmark_product INT COMMENT 'Bookmark-Product 宝贝收藏',
    ctr DECIMAL(10,6) COMMENT 'CTR 点击率',
    cpc DECIMAL(10,2) COMMENT 'CPC 点击成本',
    cpm DECIMAL(10,2) COMMENT 'CPM 拉新成本',
    roi DECIMAL(10,4) COMMENT 'ROI 投资回报率',
    cvr DECIMAL(10,6) COMMENT 'CVR 点击转化率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date_time (date_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪万相台';
