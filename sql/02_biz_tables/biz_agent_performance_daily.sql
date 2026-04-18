
-- =========================================
-- biz_agent_performance_daily.sql
-- Agent绩效日报表
-- =========================================

USE xiangwang_fliggy_system;

CREATE TABLE IF NOT EXISTS biz_agent_performance_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_batch_id BIGINT COMMENT '关联批次ID',
    agent_name VARCHAR(100) NOT NULL COMMENT 'Agent名称',
    consult_count INT COMMENT '咨询人数',
    incoming_count INT COMMENT '接入人数',
    direct_incoming_count INT COMMENT '直接接入人数',
    conversion_count INT COMMENT '转化人数',
    conversion_amount DECIMAL(14,2) COMMENT '转化金额',
    order_message_count INT COMMENT '订单消息数',
    refund_message_count INT COMMENT '退款消息数',
    customer_msg_count INT COMMENT '客服消息数',
    in_chat_time_sec INT COMMENT '在线时长(秒)',
    max_concurrent_chats INT COMMENT '最大同时接待数',
    pending_response_count INT COMMENT '未回复消息数',
    responded_count INT COMMENT '已回复消息数',
    avg_response_count INT COMMENT '平均回复数',
    first_response_sec INT COMMENT '首次响应(秒)',
    avg_response_sec DECIMAL(8,2) COMMENT '平均响应(秒)',
    total_response_time_sec INT COMMENT '总响应时长(秒)',
    stat_date DATE COMMENT '统计日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agent_name (agent_name),
    INDEX idx_stat_date (stat_date),
    INDEX idx_data_batch_id (data_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent绩效日报表';

