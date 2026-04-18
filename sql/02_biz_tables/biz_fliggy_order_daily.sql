
-- =========================================
-- biz_fliggy_order_daily.sql
-- 飞猪订单每日数据表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS biz_fliggy_order_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_batch_id BIGINT COMMENT '关联批次ID',
    stat_date DATE NOT NULL COMMENT '统计日期',
    pv BIGINT COMMENT 'PV',
    uv BIGINT COMMENT 'UV',
    paid_uv BIGINT COMMENT 'Paid UV',
    new_customer_count INT COMMENT '新客人数',
    gmv DECIMAL(14,2) COMMENT 'GMV',
    consult_count INT COMMENT '咨询量',
    consult_conversion_rate DECIMAL(8,4) COMMENT '咨询转化率',
    new_order_count INT COMMENT '新订单数',
    new_order_conversion_rate DECIMAL(8,4) COMMENT '新订单转化率',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stat_date (stat_date),
    INDEX idx_data_batch_id (data_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='飞猪订单每日数据表';

