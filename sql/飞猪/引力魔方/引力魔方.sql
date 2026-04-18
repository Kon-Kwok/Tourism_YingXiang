-- =========================================
-- 引力魔方
-- 文件: 引力魔方.xlsx
-- =========================================
USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS fliggy_gravity_rubiks_cube (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    date_time DATE NOT NULL COMMENT 'Date 时间',
    cost DECIMAL(14,2) COMMENT 'Cost 花费',
    imp BIGINT COMMENT 'IMP 展示',
    click BIGINT COMMENT 'Click 点击',
    order_count BIGINT COMMENT 'Order 订单',
    sales DECIMAL(14,2) COMMENT 'Sales 销量',
    shopping_cart BIGINT COMMENT 'ShoppingCart 加入购物车',
    bookmark_product BIGINT COMMENT 'Bookmark-Product 宝贝收藏',
    bookmark_store BIGINT COMMENT 'Bookmark-Store 店铺收藏',
    ctr DECIMAL(10,6) COMMENT 'CTR 点击率',
    cpc DECIMAL(10,2) COMMENT 'CPC 点击成本',
    cpm VARCHAR(20) COMMENT 'CPM 拉新成本',
    roi DECIMAL(10,4) COMMENT 'ROI 投资回报率',
    cvr DECIMAL(10,6) COMMENT 'CVR 点击转化率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date_time (date_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪引力魔方';
