
-- =========================================
-- biz_agent_sales_daily.sql
-- Agent销售日报表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS biz_agent_sales_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_batch_id BIGINT COMMENT '关联批次ID',
    agent_name VARCHAR(100) NOT NULL COMMENT 'Agent名称',
    consult_count INT COMMENT '咨询人数',
    incoming_count INT COMMENT '接入人数',
    booking_count INT COMMENT '预订人数',
    sales_amount DECIMAL(14,2) COMMENT '销售金额',
    order_count INT COMMENT '订单数',
    adult_count INT COMMENT '成人人数',
    child_count INT COMMENT '儿童人数',
    stat_date DATE COMMENT '统计日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_name (agent_name),
    INDEX idx_stat_date (stat_date),
    INDEX idx_data_batch_id (data_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent销售日报表';

